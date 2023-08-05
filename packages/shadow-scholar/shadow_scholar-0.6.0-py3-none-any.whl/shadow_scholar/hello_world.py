from shadow_scholar.cli import cli


@cli(name="hello-world")
def hello_world():
    msg = (
        "You have successfully installed shadow-scholar! If you want to see "
        "what other entrypoints are available, run `shadow -l`. To list all "
        "options for a given entrypoint, run `shadow <entrypoint> -h`, or "
        "`shadow <entrypoint> -r` to list its required packages. To check "
        "out how shadow-scholar responds when a package is missing, run "
        "`shadow angry-world`."
    )
    print(msg)


@cli(name="angry-world", requirements=["a-python-package-that-does-not-exist"])
def angry_world():
    ...
