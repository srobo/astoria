Astprocd
========

Astprocd is responsible for:

- Waiting for usercode drive information from :ref:`astdiskd`
- Starting and managing the :ref:`usercode lifecycle`
- Unpacking and verifying a :ref:`code bundle <Code Bundle Format>`
- Writing logs to the usercode drive
- Making logs available to other components in real time (To be `implemented <https://github.com/srobo/astoria/issues/23>`_)

Usercode Lifecycle
------------------

When a new USB is inserted, it will follow the usercode lifecycle. The possible states of the lifecycle are defined in :class:`astoria.common.messages.astprocd.CodeStatus`.

.. graphviz::

   digraph {
      "None" -> "STARTING" [ label="USB Inserted", color="darkgreen"]
      "STARTING" -> "RUNNING" [ label="robot.zip valid", color="darkgreen" ]
      "STARTING" -> "CRASHED" [ label="robot.zip invalid", color="firebrick3" ]
      "STARTING" -> "CRASHED" [ label="proc start fail", color="firebrick3" ]
      "RUNNING" -> "CRASHED" [ label="proc exit. rc > 0", color="gold"]
      "RUNNING" -> "KILLED" [ label="proc exit. rc < 0", color="orange1" ]
      "RUNNING" -> "FINISHED" [ label="proc exit. rc = 0", color="darkgreen" ]
      "CRASHED" -> "STARTING" [ label="restart", color="violetred4" ]
      "KILLED" -> "STARTING" [ label="restart", color="violetred4" ]
      "FINISHED" -> "STARTING" [ label="restart", color="violetred4" ]
   }

It is only possible for one usercode lifecycle to exist at any one time, so additional usercode USBs will be ignored if there is already a lifecycle in progress. This is the case even if the lifecycle exists in one of the stopped states.

Usercode can be executed multiple times within the lifecycle via the ``restart`` paths in the above diagram. A restart can only be triggered via mutation request.

Usercode Process Management
---------------------------

Usercode is executed as a `child process <https://linux.die.net/man/2/fork>`_ of the astprocd process.
This is managed via the ``asyncio.subprocess`` module, specifically ``asyncio.subprocess.Process``.

- :ref:`Code bundle <Code Bundle Format>` is extracted to a temporary directory and validated
- The usercode process is started as a child process
- The logger task captures ``stderr`` and ``stdout`` and writes to the log locations
- ``SIGCHLD`` is received and return code handled.
- The temporary directory is cleaned up.

Code is killed if USB is removed or by request. This manifests as a negative return code from the process.

Usercode is killed by sending ``SIGTERM``, waiting 5 seconds and then sending ``SIGKILL`` if the process still exists.


Astprocd Data Structures and Classes
------------------------------------

.. autoclass:: astoria.common.messages.astprocd.CodeStatus
    :members:

.. autoclass:: astoria.common.messages.astprocd.ProcessManagerMessage
   :members:

.. autoclass:: astoria.managers.astprocd.ProcessManager
   :members:
