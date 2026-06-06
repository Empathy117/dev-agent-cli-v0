from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension(
            "dev_agent_cli._learning_core",
            sources=["src/dev_agent_cli/learning_core.cpp"],
            language="c++",
            extra_compile_args=["-std=c++17"],
        )
    ]
)
