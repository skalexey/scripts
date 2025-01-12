## Python Utility Library
### collection
Extends the capabilities of the built-in Python collections module. It includes:
- **OrderedSet**  
	Useful collection missed in Python, that acts like a set, but allows iterating over its elements in the order they were added.
- **OrderedDict**  
	Derived from OrderedSet, extends it to implement an ordered dictionary. Despite there being an OrderedDict in Python, this one provides more features:
	- **Support for Index-Based Operations**:
		- random access by index: `my_ordered_dict[index]`
		- slicing as in lists: `my_ordered_dict[start:stop:step]`
		- `insert(index, key, value)`
		- `set_at(index, key, value)`
		- `at(index)` - returns the key-value pair at a specific index.
		- `key_at(index)`
		- `value_at(index)`
	- **Sorting Capability**  
		Sort based on keys, values, or a custom key function using `sort(by='key'/'value', reverse, key)` method.
	- **Set-Like Operations**  
		Implements `__and__`, `__xor__`, and `__ixor__` for set-like intersection and symmetric difference.
	- **Advanced pop Behavior**  
		`pop(key, default=None)` - supports a default value if the key is not found.
	- **Reversed Iteration**
	- **Custom Equality and Comparison**  
		`__eq__` and `__lt__` can compare with lists and dictionaries.
	- **Serialization Support**
- **WeakList**  
	Represents a list of elements wrapped in WeakProxy objects, allowing transparently working with the list as if it were a regular list, but avoiding taking ownership of the elements. Helps to prevent circular references and memory leaks.

### concurrency
- **ReadWriteLock, ScopedLock**  
  Python implementations for non-trivial locks.
- **Command, CommandQueue**  
  Thread-safe data change interface.
- **ParameterizedLock**  
  Wraps any lock to extend its context manager, allowing specification of parameters:  
  `"with lock(<blocking>, <timeout>):"`  
  or preset these arguments as default and continue using `"with lock:"`, suitable for debugging with specific timeout settings to identify deadlocks.
- **SafeProxy**  
  Wraps any object to access it thread-safely.
- **make_thread_safe**  
  Wraps every method of an object, including `__setattr__`, to make it execute under a lock.
- **ThreadGuard**  
  Restricts access to the object from any threads except explicitly allowed.
- **ThreadLocalProxy**  
  Makes an object appear differently to different threads by storing data into `threading.local`. Each thread has its own copy of data, while transparently using the same object and interface.

### debug
- **debug/concurrency.py**  
  Utilities for debugging different kinds of locks.
- **DebugDetector**  
  Detects when the program is suspended by a debugger. Tracks time spent debugging for use in time correction or other purposes.
- **Utilities**  
  Includes `wrap_debug_lock`, `object_by_address`, `inspect_address`, and `inspect_referrers`.

### log
- Logger with comprehensive functionality allowing customizable log messages with time, title, and any custom additions to the console, file, or log server.

### math
- Vector geometry implementation: `Line`, `Point`, `Vector`, `Point2`, `Vector2`, `Range`.

### memory
- **Buffer**  
  Can be used as a buffer for the provided data or as a virtual view of a specific segment. Supports reading by chunks.
- **LazyAllocated**  
  Acts as a proxy for an object of a specified class, created only upon first use. Stores a reference to the class or an allocation function, along with instantiation arguments.
- **WeakProxy**  
  Acts as a given object but does not take ownership. Can signal when the object is destroyed if a callback is provided.
- **Decorators**  
  - `weak_self_method`  
    Makes `self` weak, ensuring safe closure capturing using WeakProxy.
  - `weak_self_class`  
    Similar functionality for classes.
- **Callable Variants**  
  - `Callable`, `SmartCallable`, `OwnedCallable`  
    Combines and stores callable objects with their owners using weak references to prevent circular dependencies. Allows subscribing to events triggered by destruction of the owner, callable, or instance.

### net
A small library for network transport-level abstractions (`Connection`, `Server`) and concrete implementations (`TCP`, `UDP`). Enables creation of connection-agnostic systems. Includes abstract `PacketServer`.

### object
- **AttributesView**  
  Access object's attributes as a dictionary.

### profile
- **TimeProfiler**  
  Manages time measurements for specific code sections with flexible output methods.
- **WeakrefManager**  
  Wraps attributes in weak references and returns dereferenced objects upon access.
- **TrackableResource**  
  Enables visibility into creation and destruction of derived class objects, logging messages, and assigning custom functions upon destruction.

### pyside
A helper library that breaks down basic UI functionality into a set of reusable functions as well as it encapsulates complex logic of custom widgets like tables and dialogs into separate QWidget-based classes and abstract mixins ready to be used and integrated in any PySide6 application. It also provides a set of type-conversion and geometry functions, missed methods of QSize, QRect and other types, and implements Application and AutoLayout classes
- **Widgets:**  
	SliderInputWidget, RangeSliderWidget, PairWidget, RangeSliderInputWidget, LineInputWidget, CheckboxWidget, TextSpinner, CopyableLabel, ValueWidget, AbstractListWidget, ListWidget, TableWidget, SectionWidget, SpinnerDialog, ExpandableWidget, ResizeEventFilter, ExpandableDataWidget, CollapsedWidget.
- **Mixins:**  
	NegativeInfinitySliderMixin, CopyableMixin, CopyableLabelMixin, CustomAdjustSizeMixin, FitContentsMixin, ClampGeometryMixin, FitContentsListMixin, FitContentsTableMixin, CopyableListElementMixin, DataTableMixin, DeallocateExpandedWidgetMixin, DataWidgetMixin, SceneItemsMixin.
- **Application**  
	Qt implementation for utils.Application class. Defines update loop handling logic through QTimer, and integrates Qt's quit() method.
- **AutoLayout**
	Fills the gap in the Qt layout system by aligning items both horizontally and vertically if the content exceeds  the available width.
- **Helper UI flow functions**
	select_data_file, show_message, attention_message, show_spinner_message, close_spinner_message, ask_yes_no, show_input_dialog
- **Qt-specific helper functions**
	clamp_geometry, map_to_global, map_from_global, widget, global_to_view_scene_pos, parent_widget, global_geometry, global_rect, restack_widget, foreach_internals, layout_item_internals, foreach_not_hidden_child, geometry, children_geometry, foreach_geometry_influencer, collect_geometry_influencers, collect_not_hidden_children, qcolor, scale_scene_item_size, adjust_scene_items_on_resize, subtract_rects, subtract_rects_max, reduce_rect, reduce_rect_max, mixed_class.
- **Qt types missed functionality**
	QSize_gt, QSize_ge, QSize_lt, QSize_le, QSizeF_eq, QSizeF_div, QSizeF_mul, QPointF_mul_size, QRectF_mul_size, QPolygonF_mul_size.
- **Helper classes**
	CombinedMetaQtABC, ABCQt, Stub, WidgetBase.

### serialize
Aims to provide an abstract layer for object serialization and deserialization of any class. Allows to keep the class untied from a particular conversion logic, delegating the choice of the format to the user  through the use of serializer and deserializer functions passed to its `serialize()` and `deserialize()` methods. Requires classes to inherit from the Serializable base class, which enforces the necessary requirements. It provides the ability to store the class in both human-readable and storage-efficient formats. There are few serializers based on this mechanism sufficient to convert data into JSON or a database row.

### user_input
A simple and often used set of functions such as ask_`input()` and `ask_yes_no()` for getting data from a user. Implements CLI and Qt versions, keeping UI flow free from concrete implementations.

### application.py
Defines the Application class, which combines multiple mechanics and system features—such as termination signal handling, an `update(dt) loop`, and utility methods like `do_in_main_thread(f)` and `add_on_update(f)`.

### module system
A set of classes and functions that allow to create a modular application structure with ability to deliver messages and call functions on all the modules at once, dedicating a separate data file for storing settings and configuration of each module. It includes the following components:
- **Module**
	A base class for all modules. Automatically dedicates a string name for the module converting its class name to snake case. Implements the settings logic and interface.
- **ModuleManager**
	Maintains a list of all modules, managing their registration, ensuring the uniqueness of their names, providing access to them by name, and allowing to call a function on all the modules at once.

### plugin system
An extension of the module system that allows to create automatically detectable and loadable self-sufficient modules, allowing to add new functionality to the application without a need to change its code.
- **PluginManager**
Loads and holds all the plugins, ensuring following naming conventions, and architecture.
- **Plugin**
Just a module in essence, but having a separate class allows to distinguish between the regular modules and plugins, and have a clear file organization.
- **ApplicationContext**
Serves as a hub for shared resources—such as settings_manager, plugin_manager, data_manager, session_manager, main_window, and the application instance—making them accessible to any module.

### asyncio_utils.py
Utility functions for working with asyncio, specifically:
- `get_event_loop()` - get the currently running loop, or create a new one and return it
- `result(task_or_future)` - universal function to get the result of a task or a future, completing it from a non-async code through task_or_future.get_loop().run_until_complete(task_or_future).
- `task(coro_or_task)` - always returns asuncio.Task object correspondent to the given coro. If the argument is the task, just returns it.
- `create_task_threadsafe(loop, coro, loop_lock, on_done=None)` - guaranteedly creates a task in the given loop for the given coro from any thread.
- `collect_results(tasks_or_futures)` - returns a tuple of lists (done, not_done, results).

### class_utils.py
Implements such functions as:
- `class_path(cls_or_name)`
- `class_name(cls_or_path)`
- `find_class(class_path_or_name, globals=None)`

### context.py
Defines GlobalContext class, that implements a global reference to an object of the derived class that holds shared data, therefore reducing coupling between separate modules and systems.

### file.py
Provides a set of functions for working with files:
- `backup_path(path, datetime=None, date_format=None)` - Generates a unique backup name with date and time and returns it as a path in the same directory as the original file.
- `gen_free_path(path=None, gen_func=None)` - Generates a unique file name by appending a counter or using a custom generation function and returns it as a path in the same directory as the original file.
- `restore(backed_path, original_path)` - Restores a backup file to its original location with additional checks for integrity and safety of this operation.
- `backup(path, datetime=None, date_format=None)` - Creates a backup of a file by copying it to a new location with a timestamped unique name. Performs additional checks for the integrity and safety of this operation.
- `verify_copy(source_path, destination_path)` - Verifies the integrity of a copied file by comparing its size and modification time.
- `is_open(fpath)` - Checks if a file at the given path is open by attempting to rename it.

### function.py
Utils for working with functions:
- `params(func, out=None, filter=None)` - returns a dictionary with input parameters of a function with their default values, excluding variadic aliases (*args and **kwargs) if possible, optionally filtering out some of them based on the given predicate.
- `args(out=None, validate=True, custom_frame=None, extract_args=None, extract_kwargs=None)` - collects arguments passed to the caller's function, optionally validating and extracting additional arguments or keyword arguments.
- `msg(message=None, args_format=None, frame=None, ignore_first=None)` - Constructs a message string prefixed with the current function's name and arguments in one of the formats: "names", "values", "kw", where "kw" displays all the arguments, including positional, in the name=value format.
- `msg_kw(message=None, frame=None)` - Calls msg() with the "kw" format.
- `msg_v(message=None, frame=None)` - Calls msg() with the "values" format.
- `glue(*funcs)` - Combines multiple functions into a single one.

### method.py
utils for working with methods:
- `args()`, `params()`, `msg()`, `msg_kw()`, `msg_v()` - inherit implementation from utils.function, but skipping the first argument (self or cls).
- `is_first_arg_valid(arg)` - Checks if the first argument of a method is a valid class or instance.
- `filter_params(all_attrs, method)` - Separates parameters of the method from the given dictionary.
- `chain_params(method_or_func, cls=None, mro_end=None, out=None, filter=None)` - Collects parameters from all implementations of a method in a class hierarchy.
- `chain_args(base_class=None, out=None, validate=True, custom_frame=None)` - Goes through the stack and collects the arguments passed to all the implementations of the caller method in the caller class hierarchy up to the base_class.

### import_utils.py
- `is_module_path(path)` - Checks if the given path corresponds to an existing Python module. Helps distinguish module paths from class paths.
- `module_cache()` - Finds all the modules in the Python module search path and stores their paths. Used by `is_module_path()` to distinguish module paths from class paths. Works asynchronously as this task is quite demanding for big projects.
- `collect_search_paths()` - Returns a set of all the paths where Python searches for modules.
- `find_or_import_class(class_path)` - Searches for a class by its fully qualified path (e.g., '`module.submodule.ClassName')` among imported modules, imports if not found, and then returns it.

### lazy_loader.py
Allows to access symbols from a user's module without explicitly importing them, as they were already imported. If the accessed symbol is a not-yet-imported module, the loader imports it, achieving "lazy import" or "import on demand" behavior. It is useful for removing circular dependencies and speeding up the application startup time.

### `inspect_utils.py`
- **`signature_input(func, out=None, filter=None)`** - Returns a dictionary with parameters of a function with their default values, or `VAR_KEYWORD`/`VAR_POSITIONAL` for variadic aliases (`*args` and `**kwargs`). Optionally filters out some of them based on the given predicate.
- **`current_function_signature(custom_frame=None, args_format=None, ignore_first=None)`** - Returns a string representing the current function's signature.
- **`signature_str(func, cls=None, frame=None, args_format=None, ignore_first=None)`** - Returns a string representation of a given function's signature.
- **`frame_function(frame)`** - Returns a function of the given frame.
- **`module_name(frame=None)`** - Gets the module name where the frame is called.
- **`class CallInfo`** - Extended information about the call stack frame with attached `module_name`, `frame`, `co_name`, and:
	- Caller object, class, and method in the case of class method call and module name,
	- Function in the case of a function call.
- **`functions(obj)`** - Returns a list of functions that represent the given object. It retrieves getter and setter functions for properties, the function for methods, and the function itself for standalone functions.
- **`function(obj)`** - Retrieves the function associated with the given object. It returns function of a method, getter function of a property, and function itself for a function.
- **`cls(obj)`** - Retrieves the class of an object.

### Intrstate
Ensures the intrinsic state of an object remains unchanged by storing all user attributes in a separate _state dictionary. This approach is useful for representing a data block as an object while concealing control information from the user.

### job.py
Defines the `"Job"` concept, representing a task that progresses iteratively within an update loop until completion. Includes the implementation of `TimedJob`, with an `update(dt)` method for time-based updates.

### `json_utils.py` - Helper functions for working with JSON
- **`is_primitive(value)`** - Checks if a value is one of `int`, `str`, `bool`, `float`, or `None`.
- **`is_dictionary(value)`** - Checks if a value is a dictionary or `OrderedDict`.
- **`is_list(value)`** - Checks if a value is a list or tuple.
- **`is_collection(value)`** - Checks if a value is a dictionary or a list (collection).
- **`is_serializable(value)`** - Checks if a value is JSON-serializable (primitive or collection).
- **`load(string)`** - Pre-checks whether the given string is valid JSON before attempting to load it in debug mode. Returns `None` instead of raising an exception, making it suitable for non-exception designs.
- **`stringify(obj, default=None, throw=True, overwrite=False, fpath=None, backup=False, precache=True)`** - Serializes a Python object into a JSON string or writes it to a file, with error handling and safety options to back up the data that would be overwritten, either in a file or memory.

### `lang.py`
- **`is_primitive(value)`** - Checks if a value is of a primitive type (`int`, `float`, `str`, `bool`, or `bytes`).
- **`extract_self(bound_method)`** - Extracts the object to which a method is bound.
- **`clear_resources(obj)`** - Sets all the attributes of an object to `None`, or calls `obj.clear()` if `obj` is a dictionary. Useful for triggering garbage collection in the case of circular references.
- **`class NoValue`** - Represents a value that has not been set. Useful for default arguments where `None` is a valid value.
- **`safe_super(cls, inst)`** - An extended version of `super()`, designed to prevent exceptions when called at the final point in the MRO. Reduces coupling by abstracting away uncertainties in the class hierarchy.
- **`getattr_noexcept(obj, name, default=NoValue)`** - Safely retrieves an attribute value without exceptions. Returns `default` if the attribute does not exist.
- **`compare_exceptions(e1, e2)`** - Compares two exceptions for equality by type and arguments.
- **`safe_enter(func)`** - Decorator for `__enter__` that ensures `__exit__` is always called, even in the case of an exception in `__enter__`.


### parameterized_context_manager.py
Defines base and wrapper classes that allow to specify all the parameters in the context manager call, like "with lock(timeout, blocking):", or preset these arguments as default and continue using just "with lock:" as usual, that is very suitable for debugging by setting timeouts for all the locks to find which one causes a deadlock without changing their usage code.

### Proxy
Propagates all operations to the wrapped object. Used as a base class for different kinds of object wrappers and references.

### SignalRegistry
Allows to register more than one handler per a signal.

### sqlite.py
Utilities for working with SQLite databases, providing functionality for schema modifications, full database backups, and common operations like data insertion, updates, and queries. Offers thread-safe higher-level interfaces that encapsulate resource allocation and management. It also includes monolite interface with self-sufficient functions for one-line operations.

### string.py
Helper functions for strings processing, including: to_camel_case(str, delimiter=None),  to_snake_case(str), is_datetime(str)

### subscription.py
Contains such classes as:
- **`Subscription`** - basic subscription implementation that allows a set of functions or any callables to be invoked through `sub.notify()` call. It has such methods as `subscribe`, `unsubscribe`, `notify`, `wait`, `asyncio_wait`.
- **`OneTimeSubscription`** - Extends `Subscription` to ensure notifications occur only once, and stores the result of the notification as a value passed to `notify(result)` call. Provides future-like interface with `set_result(res)` and `result()` methods.
- **`Event`** - a specialization of `OneTimeSubscriptionBase` where the result acts as a flag indicating whether the notification has occurred. Provides `set()` and `is_set()` methods.

### TaskScheduler
Aims to provide a simple interface to maintain a queue of functions to run in non-blocking manner, allowing the running thread to continue handling other tasks, delegating the queue maintainance to the underlying mechanisms of `TaskScheduler` based on asyncio. Provides not async interface, allowing it to be used within ordinary (not async) functions, and ensures thread safety of all operations.
- **`schedule_task(self, async_function, max_queue_size=0, *args, **kwargs)`** - runs a function, or puts it in the queue but no more than `<max_queue_size>` times unique for this function.
- **`run_parallel_task(self, async_function)`** - runs a function even if there is already running one.
- **`update(self, dt)`** - entry point for tasks execution. Executes the tasks in order suspending after no more than `<dt>` seconds. Useful for `update(dt)` loops.
- **`run_until_complete(self, awaitable)`** - executes an awaitable (such as an `asyncio.Task`, coroutine, or future) until completion, handling precautions for the currently running event loop and threading context.
- **`run_until_complete_for(self, tasks_or_futures, timeout)`** - runs multiple awaitables with `run_until_complete()` for a limited time, returning their results.
- **`wait(self, future)`** - waits for a specific future to complete and returns its result.
- **`wait_for(self, future, timeout)`** - waits for a specific future to complete within the given timeout. Returns a `WaitForResult` object containing the results of the future (if successful) or indicating a timeout.
- **`wait_all_tasks(self, timeout=None)`** - Waits for all scheduled tasks to complete, with an optional timeout.
- **`complete_all_tasks(self, timeout=None)`** - calls `wait_all_tasks()` and then `cancel_all_tasks()` if the timeout is exceeded.
- **`cancel_all_tasks(self)`** - cancels all running and scheduled tasks.
- **`registered_task_count(self, function=None)`** - returns the total number of tasks currently registered, optionally filtered by function.
- **`queue_size(self, function=None)`** - returns the size of the task queue, optionally filtered by function.
- **`task_in_work_count(self, function=None)`** - returns the number of tasks currently in progress, optionally filtered by function.
- **`loop()`, `tasks()`** - access to the asyncio resources.

### timed_loop.py
Useful utility for running a loop for a fixed time. E.g.:
```python
for state in timed_loop(3):
	<do something>
	if state.attempt > limit:
		break
if state.timedout:
	raise RuntimeError("Failed to complete the task in time.")
```
where state is a structure with fields:
- `timeout` - contains the number passed to `timed_loop()`.
- `last_time` - the time of the last iteration.
- `elapsed_time` - the time passed since the start of the loop.
- `attempt` - the number of the current iteration.
- `timedout` - a flag indicating whether the loop has stopped due to a timeout.
