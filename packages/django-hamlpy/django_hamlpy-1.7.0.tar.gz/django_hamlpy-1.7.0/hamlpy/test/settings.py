DEBUG = True

DATABASES = {}

INSTALLED_APPS = ("hamlpy",)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["hamlpy/test/templates"],
        "OPTIONS": {
            "loaders": [
                "hamlpy.template.loaders.HamlPyFilesystemLoader",
                "hamlpy.template.loaders.HamlPyAppDirectoriesLoader",
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            "debug": True,
        },
    }
]

SECRET_KEY = "tots top secret"
