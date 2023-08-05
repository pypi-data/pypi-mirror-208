from dequeai.dequeai_run import Run

run = Run()


def init( user_name, api_key, project_name):
    run.init(user_name=user_name, api_key=api_key, project_name=project_name)

def finish():
    run.finish()

def log( data, step=None, commit=True):
    run.log(data=data, step=step, commit=commit)

def log_hyperparams( hyperparams):
    run.log_hyperparams(hyperparams=hyperparams)

def log_artifact(artifact_type, path):
    run.log_artifact(artifact_type=artifact_type, path=path)

def load_artifact(artifact_type, run_id):
    run.load_artifact(artifact_type=artifact_type, run_id=run_id)

def register_artifacts(latest=True, label=None, tags=None):
    run.register_artifacts(latest=latest, label=label, tags=tags)

def compare_runs(project_name, metric_key):
    run.compare_runs(project_name=project_name, metric_key=metric_key)

def read_best_run(project_name, metric_key):
    run.read_best_run(project_name=project_name, metric_key=metric_key)



