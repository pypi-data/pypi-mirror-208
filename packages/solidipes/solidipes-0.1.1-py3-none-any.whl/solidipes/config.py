solidipes_dirname = ".solidipes"
study_metadata_filename = "study_metadata.yaml"
study_medatada_mandatory_fields = [
    "title",
    "upload_type",
    "description",
    "creators",
    "keywords",
]
mimes_filename = "mimes.yaml"
zenodo_infos_filename = "zenodo_infos.yaml"
ignore_filename = "ignore.yaml"
default_ignore_patterns = [
    "*~",
    ".git",
    ".gitattributes",
    ".gitignore",
    ".ipynb_checkpoints",
    "__pycache__",
    ".renku",
    ".streamlit",
    f"{solidipes_dirname}",
]
