# Solution to the concurrent bridge problem.


The goal is to ensure that pedestrians, northbound cars, and southbound cars do not cross the bridge at the same time. Instead, they must yield to one another to avoid conflicts while also preventing excessive waiting times.

The attached image contains a justification of the code's development and its correctness. The .py file contains the final version of the code.

The code is fully functional and correctly handles all cases, ensuring that no starvation occurs and that all vehicles and pedestrians can cross in both directions. To prevent starvation, the solution implements a turn-based system, which is thoroughly explained in the provided documentation.

The implementation is based on a generalization of the classic readers-writers problem, a well-known challenge in concurrent programming. From this foundation, a turn-based mechanism is introduced to balance fairness among different types of traffic.

All key ideas and design choices in the code are documented in the explanation file.

This problem is an example of concurrent programming, where multiple entities (pedestrians and vehicles) need to share a limited resource (the bridge) without conflicts or inefficiencies. Synchronization mechanisms, such as semaphores or locks, are used to control access, ensuring fairness and preventing issues like deadlocks or starvation.
