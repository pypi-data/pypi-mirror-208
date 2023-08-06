from looqbox.class_loader.class_loader import ClassLoader

def SqlThreadManager(*args, **kwargs):
    return ClassLoader("SqlThreadManager", "looqbox.database.objects.sql_thread_manager").call_class(*args, **kwargs)
