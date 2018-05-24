var rawResponseBody = '';
var xhr = new XMLHttpRequest();

var renderFunction = renderTabular;
var streamedResponse = false;

String.prototype.replaceAll = function(search, replacement) {
    var target = this;
    return target.split(search).join(replacement);
};

function runCommand() {
    var sqlExpression = editor.getValue();
    var upperSqlExpression = sqlExpression.toUpperCase();
    var sqlExpression = editor.getValue();
    if (upperSqlExpression.startsWith("SELECT ") || upperSqlExpression.startsWith("PRINT ")) {
        streamedResponse = true;
        // execute KSQL interactive streaming query
        sendRequest("/query", sqlExpression)
    } else {
        // execute KSQL statement
        streamedResponse = false;
        sendRequest("/ksql", sqlExpression)
    }
}

function displayServerVersion() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var serverVersionResponse = JSON.parse(this.responseText);
            document.getElementById("copyright").innerHTML = "(c) Confluent Inc., KSQL server v" + serverVersionResponse.KsqlServerInfo.version
        }
    };
    xhr.open("GET", "/info", true);
    xhr.send();
}

function sendRequest(resource, sqlExpression) {
    xhr.abort();

    var properties = getProperties();

    xhr.onreadystatechange = function() {
        if (xhr.response !== '' && ((xhr.readyState === 3 && streamedResponse) || xhr.readyState === 4)) {
            rawResponseBody = xhr.response;
            renderResponse();
        }
        if (xhr.readyState === 4 || xhr.readyState === 0) {
            document.getElementById('request_loading').hidden = true;
            document.getElementById('cancel_request').hidden = true;
        }
    };

    var data = JSON.stringify({
        'ksql': sqlExpression,
        'streamsProperties': properties
    });

    console.log("Sending:" + data)

    document.getElementById('cancel_request').hidden = false;
    document.getElementById('request_loading').hidden = false;
    xhr.open('POST', resource);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(data);
}

function cancelRequest() {
    //var responseElement = document.getElementById('response');
    //var response = responseElement.innerHTML;
    xhr.abort();
    //responseElement.innerHTML = response;
}

function renderResponse() {
    var renderedBody = '';
    if (streamedResponse) {
        // Used to try to report JSON parsing errors to the user, but
        // since printed topics don't have a consistent format, just
        // have to assume that any parsing error is for that reason and
        // we can just stick with the raw message body for the output
        var splitBody = rawResponseBody.split('\n');
        for (var i = 0; i < splitBody.length; i++) {
            var line = splitBody[i].trim();
            if (line !== '') {
                try {
                    var parsedJson = JSON.parse(line);
                    renderedBody += renderFunction(parsedJson);
                } catch (SyntaxError) {
                    renderedBody += line;
                }
                renderedBody += '\n';
            }
        }
    } else {
        try {
            var parsedJson = JSON.parse(rawResponseBody);
            renderedBody = renderFunction(parsedJson);

            if (renderedBody == "") {
                updateFormat(renderPrettyJson)
                renderFunction = renderTabular;
                return;
            }


        } catch (SyntaxError) {
            console.log('Error parsing response JSON:' + SyntaxError.message);
            console.log(SyntaxError.stack);
            renderedBody = rawResponseBody;
        }
    }
    response.setValue(renderedBody);
    response.gotoLine(1);
}

function renderTabular(parsedBody) {
    response.session.setMode("ace/mode/json");

    if (Array.isArray(parsedBody)) {
        // The response is a list of statement responses
        var result = [];
        for (var i = 0; i < parsedBody.length; i++) {
            result.push(renderTabularStatement(parsedBody[i]));
        }
        return result.join('\n\n');
    } else if (parsedBody instanceof Object) {
        // The response is either an error or a streamed row
        var errorMessage = parsedBody.message || parsedBody.errorMessage;
        if (errorMessage) {
            return parsedBody.message;
        } else if (parsedBody.row) {
            var result = [];
            var columns = parsedBody.row.columns;
            for (var i = 0; i < columns.length; i++) {
                // TODO: Figure out how to handle arrays/maps here...
                result.push(columns[i].toString());
            }
            return ' ' + result.join(' | ') + ' ';
        } else {
            throw SyntaxError;
        }
    } else {
        throw SyntaxError;
    }
}

function getObjectProperties(object) {

    var rowValues = [];

    for (var property in object) {
        if (!object.hasOwnProperty(property)) {
            continue;
        }
        rowValues.push([property, object[property].toString()]);
    }
    return rowValues;
}

function getAutoColsAndRows(object) {

    var cols = [];

    Object.keys(object[0]).forEach(function(key) {
        cols.push(upperCaseFirst(key))
    });

    var rows = [];

    object.forEach(function(item) {
        var row = []
        Object.values(item).forEach(function(value) {
            // stringify the value
            if (isPrimitive(value)) {
                value = value + "";
            } else {
                value = JSON.stringify(value);
            }

            row.push(value)
        });
        rows.push(row);
    })
    return [cols, rows];
}

function renderTabularStatement(statementResponse) {
    var autoColAndRows;
    var columnHeaders, rowValues;

    if (statementResponse.properties) {
        columnHeaders = ['Property', 'Value'];
        rowValues = getObjectProperties(statementResponse.properties.properties);

    } else if (statementResponse.kafka_topics) {
        autoColAndRows = getAutoColsAndRows(statementResponse.kafka_topics.topics)
    } else if (statementResponse.streams) {
        autoColAndRows = getAutoColsAndRows(statementResponse.streams.streams)
    } else if (statementResponse.tables) {
        autoColAndRows = getAutoColsAndRows(statementResponse.tables.tables)
    } else if (statementResponse.queries) {
        autoColAndRows = getAutoColsAndRows(statementResponse.queries.queries)
    } else if (statementResponse.error) {
        return renderYaml(statementResponse)
    } else if (statementResponse.description) {
        return renderYaml(statementResponse)
    } else if (statementResponse.currentStatus) {
        return renderYaml(statementResponse)
    } else if (statementResponse.setProperty) {
        var innerBody = statementResponse.setProperty;
        columnHeaders = ['Property', 'Prior Value', 'New Value'];
        rowValues = [
            [innerBody.property, innerBody.oldValue, innerBody.newValue]
        ];

    } else {
        throw SyntaxError;
    }
    if (autoColAndRows != null) {
        return renderTable(autoColAndRows[0], autoColAndRows[1]);
    } else {
        return renderTable(columnHeaders, rowValues);
    }


}

function renderTable(columnHeaders, rowValues) {
    var lengths = [];

    var cols = [];

    columnHeaders.forEach(function(item) {
        lengths.push(item.length);
    })

    if (!rowValues || rowValues.length === 0) {
        return renderTableRow(columnHeaders, lengths);
    }


    rowValues.forEach(function(row) {
        row.forEach(function(item) {
            for (var j = 0; j < row.length; j++) {
                lengths[j] = Math.max(lengths[j], row[j].length);
            }
        })
    })

    var lengthsSum = lengths[0] + 2;
    for (var i = 1; i < lengths.length; i++) {
        lengthsSum += lengths[i] + 3;
    }

    var result = [
        renderTableRow(columnHeaders, lengths),
        Array(lengthsSum + 1).join('-')
    ];
    for (var i = 0; i < rowValues.length; i++) {
        result.push(renderTableRow(rowValues[i], lengths));
    }

    return result.join('\n');
}

function renderTableRow(values, lengths) {
    var result = [];
    for (var i = 0; i < values.length; i++) {
        result.push(pad(values[i], lengths[i] || 0));
    }
    return ' ' + result.join(' | ') + ' ';
}

function pad(str, len) {
    if (str.length >= len) {
        return str;
    }
    var pad = Array(len - str.length + 1).join(' ');
    return str + pad;
}

function renderPrettyJson(parsedBody) {
    response.session.setMode("ace/mode/json");
    return JSON.stringify(parsedBody, null, 2);
}

function renderCompactJson(parsedBody) {
    response.session.setMode("ace/mode/json");
    return JSON.stringify(parsedBody);
}
function renderYaml(parsedBody) {
    response.session.setMode("ace/mode/yaml");
    return json2yaml(parsedBody).replaceAll("\\x20"," ").replaceAll("\\x2C",",").replaceAll("\\x3B",";").replaceAll("\\x27","'").replaceAll("\\x3A",":").replaceAll("\\x28","(").replaceAll("\\x29",")");
}

function updateFormat(newRenderFunction) {
    renderFunction = newRenderFunction;
    if (rawResponseBody !== '') {
        renderResponse();
    }
}

function upperCaseFirst(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
function isPrimitive(test) {
    return (test !== Object(test));
};

function addNewProperty() {
    var key = document.createElement('input');
    key.type = 'text';
    key.placeholder = 'key';
    key.classList.add('property-key');

    var value = document.createElement('input');
    value.type = 'text';
    value.placeholder = 'value';
    value.classList.add('property-value');

    var deleteButton = document.createElement('button');
    deleteButton.appendChild(document.createTextNode('X'));

    var propertySpan = document.createElement('span');
    propertySpan.classList.add('property');

    propertySpan.appendChild(key);
    propertySpan.appendChild(document.createTextNode(' '));
    propertySpan.appendChild(document.createTextNode('='));
    propertySpan.appendChild(document.createTextNode(' '));
    propertySpan.appendChild(value);
    propertySpan.appendChild(document.createTextNode(' '));
    propertySpan.appendChild(deleteButton);

    var propertyDiv = document.createElement('div');
    propertyDiv.classList.add('property');

    propertyDiv.appendChild(propertySpan);

    var propertiesElement = document.getElementById('properties');
    propertiesElement.appendChild(propertyDiv);

    deleteButton.onclick = function() {
        propertiesElement.removeChild(propertyDiv);
    }
}

function getProperties() {
    var properties = {};
    var key, value;
    var propertyElements = document.getElementById('properties').children;
    for (var i = 0; i < propertyElements.length; i++) {
        var propertyDiv = propertyElements[i];
        if (!propertyDiv.classList.contains('property')) {
            continue;
        }
        var propertyDivChildren = propertyDiv.children;
        for (var j = 0; j < propertyDivChildren.length; j++) {
            var propertySpan = propertyDivChildren[j];
            if (!propertySpan.classList.contains('property')) {
                continue;
            }
            var propertySpanChildren = propertySpan.children;
            for (var k = 0; k < propertySpanChildren.length; k++) {
                var propertyInput = propertySpanChildren[k];
                if (propertyInput.classList.contains('property-key')) {
                    key = propertyInput.value.trim();
                } else if (propertyInput.classList.contains('property-value')) {
                    value = propertyInput.value.trim();
                }
            }
        }
        if (key === '') {
            continue;
        }
        properties[key] = value;
    }
    return properties;
}

window.onload = addNewProperty;