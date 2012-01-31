Continuous Integration with Jenkins
===================================

Engine uses a `Jenkins`_ server to automate development tasks. The Jenkins
front-end is at http://jenkins.x7.org. You must have an
account on `Launchpad`_ to be able to access the X7 Jenkins site.

Jenkins performs tasks such as:

`gate-engine-unittests`_
    Run unit tests on proposed code changes that have been reviewed.

`gate-engine-pep8`_
    Run PEP8 checks on proposed code changes that have been reviewed.

`gate-engine-merge`_
    Merge reviewed code into the git repository.

`engine-coverage`_
    Calculate test coverage metrics.

`engine-docs`_
    Build this documentation and push it to http://engine.x7.org.

`engine-pylint`_
    Run `pylint <http://www.logilab.org/project/pylint>`_ on the engine code and
    report violations.

`engine-tarball`_
    Do ``python setup.py sdist`` to create a tarball of the engine code and upload
    it to http://engine.x7.org/tarballs

.. _Jenkins: http://jenkins-ci.org
.. _Launchpad: http://launchpad.net
.. _gate-engine-merge: https://jenkins.x7.org/view/Engine/job/gate-engine-merge
.. _gate-engine-pep8: https://jenkins.x7.org/view/Engine/job/gate-engine-pep8
.. _gate-engine-unittests: https://jenkins.x7.org/view/Engine/job/gate-engine-unittests
.. _engine-coverage: https://jenkins.x7.org/view/Engine/job/engine-coverage
.. _engine-docs: https://jenkins.x7.org/view/Engine/job/engine-docs
.. _engine-pylint: https://jenkins.x7.org/job/engine-pylint
.. _engine-tarball: https://jenkins.x7.org/job/engine-tarball
