.. _contributing_guide :

How to Contribute
-----------------

General Guidelines
~~~~~~~~~~~~~~

When submitting a pull request (PR), please use the following guidelines:

* Make sure your code respects existing formatting conventions. In general, follow
  the same coding style as the code that you are modifying.
* Do add/update documentation appropriately for the change you are making.
* If you are introducing a new feature you may want to first submit your idea
  for feedback to the `Confluent mailing list <mailto:partner-support@confluent.io>`_.
* Non-trivial features should include unit tests covering the new functionality.
* Bugfixes should include a unit test or integration test reproducing the issue.
* Try to keep pull requests short and submit separate ones for unrelated
  features, but feel free to combine simple bugfixes/tests into one pull request.
* Keep the number of commits small and combine commits for related changes.
* Each commit should compile on its own and ideally pass tests.
* Keep formatting changes in separate commits to make code reviews easier and
  distinguish them from actual code changes.

GitHub Workflow
~~~~~~~~~~~~~~

1. Fork the confluentinc/cp-docker-images repository into your GitHub account

  https://github.com/confluentinc/cp-docker-images/fork

2. Clone your fork of the GitHub repository

  .. sourcecode:: bash

    $ git clone git@github.com:<username>/cp-docker-images.git

  Note: replace `<username>` with your GitHub username.

3. Add a remote to keep up with upstream changes

  .. sourcecode:: bash

    $ git remote add upstream https://github.com/confluentinc/cp-docker-images.git

  If you already have a copy, fetch upstream changes

  .. sourcecode:: bash

    $ git fetch upstream
  
4. Create a feature branch to work in

  .. sourcecode:: bash

    $ git checkout -b feature-xxx remotes/upstream/master

5. Work in your feature branch

  .. sourcecode:: bash
    
    $ git commit -a

6. Periodically rebase your changes

  .. sourcecode:: bash
  
    $ git pull --rebase

7. When done, combine ("squash") related commits into a single one

  .. sourcecode:: bash

    $ git rebase -i upstream/master

  This will open your editor and allow you to re-order commits and merge them:
  - Re-order the lines to change commit order (to the extent possible without creating conflicts)
  - Prefix commits using `s` (squash) or `f` (fixup) to merge extraneous commits.

8. Submit a pull-request

  .. sourcecode:: bash
    
    $ git push origin feature-xxx

  Go to your cp-docker-images fork main page

  .. sourcecode:: bash

    https://github.com/<username>/cp-docker-images

  If you recently pushed your changes GitHub will automatically pop up a
  `Compare & pull request` button for any branches you recently pushed to. If you
  click that button it will automatically offer you to submit your pull-request
  to the `confluentinc/cp-docker-images` repository.

  - Give your pull-request a meaningful title.
  - In the description, explain your changes and the problem they are solving.

9. Addressing code review comments

  Repeat steps 5. through 7. to address any code review comments and
  rebase your changes if necessary.

  Push your updated changes to update the pull request

  .. sourcecode:: bash
    
    $ git push origin [--force] feature-xxx

  `--force` may be necessary to overwrite your existing pull request in case your
  commit history was changed when performing the rebase.

  Note: Be careful when using `--force` since you may lose data if you are not careful.

  .. sourcecode:: bash

    $ git push origin --force feature-xxx

FAQ
~~~

Help! I merged changes from upstream and cannot figure out how to resolve conflicts when rebasing!

Never fear! If you occasionally merged upstream/master, here is another way to squash your changes into a single commit:

1. First, rename your existing branch to something else, e.g. `feature-xxx-unclean`

  .. sourcecode:: bash
    
    $ git branch -m feature-xxx-unclean


2. Checkout a new branch with the original name `feature-xxx` from upstream. This branch will supercede our old one.

  .. sourcecode:: bash

  $ git checkout -b feature-xxx upstream/master

3. Then merge your changes in your original feature branch `feature-xxx-unclean` and create a single commit.

  .. sourcecode:: bash

    $ git merge --squash feature-xxx-unclean
    $ git commit

4. You can now submit this new branch and create or replace your existing pull request.

  .. sourcecode:: bash
    
    $ git push origin [--force] feature-xxx:feature-xxx
