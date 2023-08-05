#!/bin/env python
################################################################
import base64
import fnmatch
import os

import streamlit as st
import streamlit.components.v1 as components

################################################################
from git import InvalidGitRepositoryError, Repo
from streamlit_ace import st_ace
from streamlit_tree_select import tree_select

# Must import explicitely from "solidipes" to work in Streamlit
from solidipes.loaders.file import File
from solidipes.loaders.mime_types import extension2mime_type, is_valid_extension, mime_types2extensions
from solidipes.scanners.scanner import Scanner, for_each_file
from solidipes.utils import (
    get_git_repository,
    get_git_root,
    get_mimes,
    get_solidipes_directory,
    get_study_metadata,
    set_mimes,
    set_study_metadata,
)

################################################################
command = "report"
command_help = "generate report from directory"
################################################################
jupyter_icon_filename = os.path.join(os.path.dirname(__file__), "jupyter_logo.png")
_jupyter_icon = base64.b64encode(open(jupyter_icon_filename, "rb").read()).decode("utf-8")


def transform_to_subtree(h, subtree=""):
    tree = []
    for name, f in h.items():
        if isinstance(f, dict):
            current_dir = os.path.join(subtree, name)
            s = transform_to_subtree(f, current_dir)
            if s:
                tree.append({"label": name, "value": current_dir, "children": s})
            else:
                tree.append({"label": name, "value": current_dir})
    return tree


################################################################


################################################################


class StateWrapper:
    def __init__(self, f):
        if "GUI_files" not in st.session_state:
            st.session_state["GUI_files"] = {}

        self.key = "solidipes_state_GUI_" + f.file_info.path
        self.f = f

        if self.key not in st.session_state["GUI_files"]:
            # st.write(f'create key {self.key}')
            st.session_state["GUI_files"][self.key] = {}
        self.logger = None

    def set_logger(self, foo):
        # self.logger = foo
        pass

    def __getattribute__(self, name):
        if name in ["key", "f", "logger", "set_logger"]:
            return super().__getattribute__(name)

        if name not in st.session_state["GUI_files"][self.key]:
            st.session_state["GUI_files"][self.key][name] = None
        return st.session_state["GUI_files"][self.key][name]

    def __setattr__(self, name, value):
        if name in ["key", "f", "logger", "set_logger"]:
            super().__setattr__(name, value)
            return
        if self.key not in st.session_state["GUI_files"]:
            st.session_state["GUI_files"][self.key] = {}
        st.session_state["GUI_files"][self.key][name] = value
        if self.logger is not None:
            self.logger(self.f.file_info.path, f"{name} -> {value}")


################################################################


class FileWrapper:
    def __init__(self, f):
        self.state = StateWrapper(f)
        self.f = f

    def __getattr__(self, name):
        if name in ["state", "f"]:
            return super().__getattr__(name)

        return getattr(self.f, name)


################################################################


class Report:
    def __init__(self):
        self.file_wildcard = "*"
        self.file_error_checkbox = None

        self.git_origin = None
        self.git_root = None
        self.git_repository = None
        try:
            self.git_root = get_git_root()
            self.git_repository = get_git_repository()
            self._set_gitlab_uri()
        except InvalidGitRepositoryError:
            pass

        self.scanner = Scanner()
        st.set_page_config(layout="wide")
        self.createLayouts()

    def createLayouts(self):
        self.progress_layout = st.sidebar.empty()
        self.update_buttons = st.sidebar.container()
        self.file_selector = st.sidebar.container()
        self.path_selector = st.sidebar.container()
        if self.git_repository is not None:
            self.git_control = st.sidebar.container()
        self.jupyter_control = st.sidebar.container()
        self.env_layout = st.sidebar.container()
        self.options = st.sidebar.expander("Options")

        self.main_layout = st.container()
        self.logs = self.main_layout.container()
        self.global_message = self.main_layout.container()
        self.header_layout = self.main_layout.container()
        self.zenodo_layout = self.main_layout.container()
        self.zenodo_publish_layout = self.main_layout.container()
        self.gitlab_issues = self.main_layout.container()
        self.files_container = self.main_layout.container()

    def scan_files(self, paths):
        found = self.scanner.scan_dirs(paths, recursive=False)
        return found

    def _set_gitlab_uri(self):
        dir_path = os.getcwd()
        self.git_repository = Repo(dir_path, search_parent_directories=True)
        remotes = self.git_repository.remotes
        if "origin" not in remotes:
            return
        git_origin = [e for e in remotes.origin.urls][0]
        if git_origin.startswith("git@"):
            git_origin = git_origin.replace("git@", "")
            _split = git_origin.split(":")
            git_origin = "https://" + _split[0] + "/gitlab/" + _split[1]
        self.git_origin = git_origin.replace(".git", "")

    def alternative_parser(self, e):
        return []

    def add_log(self, mesg):
        self.log_layout.text(mesg)

    def load_file(self, e):
        if not e.state.loaded:
            try:
                e.load_all()
            except Exception as err:
                e.errors += ["Error during import<br>" + str(err)]
            e.errors += self.alternative_parser(e)
            e.state.valid = e.valid_loading()
            e.state.errors = e.errors
            e.state.loaded = True

    def get_file_title(self, e):
        path = e.file_info.path
        file_title = f"{path}"

        if e.state.valid:
            title = ":white_check_mark: &nbsp; &nbsp;" + file_title
        else:
            title = ":no_entry_sign: &nbsp; &nbsp; " + file_title
            title += "&nbsp; &nbsp; :arrow_backward: &nbsp; &nbsp; "
            title += f"**{e.file_info.type.strip()}**"

        if e.state.view:
            title += "&nbsp; :open_book:"

        return title

    def get_file_edit_link(self, e):
        _path = e.file_info.path
        while os.path.islink(_path):
            dirname = os.path.dirname(_path)
            _path = os.path.join(dirname, os.readlink(_path))

        url = self.git_origin + "/-/edit/master/data/" + _path
        return url

    def mime_type_information(self, e, layout, main_layout):
        valid_ext = is_valid_extension(e.file_info.path, e.file_info.type)
        if not e.state.valid and not valid_ext:
            type_choice_box = layout.empty()
            type_choice = type_choice_box.container()
            sel = type_choice.radio(
                "Type selection",
                options=["extension", "mime"],
                key="type_sel_" + e.file_info.path,
                horizontal=True,
            )

            choice = None
            if sel == "mime":
                possible_types = [e for e in mime_types2extensions.keys()]
                choice = type_choice.selectbox(
                    "type",
                    ["Select type"] + possible_types,
                    key="mime_" + e.file_info.path,
                )
            else:

                def format_types(x):
                    if x == "Select type":
                        return x
                    return f"{x} ({extension2mime_type[x]})"

                possible_types = [e for e in extension2mime_type.keys()]
                choice = type_choice.selectbox(
                    "extension",
                    ["Select type"] + possible_types,
                    format_func=format_types,
                    key="mime_" + e.file_info.path,
                )
                if choice != "Select type":
                    choice = extension2mime_type[choice]

            if choice != "Select type":
                st.write(choice)
                confirm = main_layout.button(
                    f"Confirm change type {choice} -> {mime_types2extensions[choice]}",
                    type="primary",
                    use_container_width=True,
                )
                if confirm:
                    mimes = get_mimes()
                    mimes[e.file_info.path] = choice
                    set_mimes(mimes)
                    self.clear_session_state()
                    st.experimental_rerun()
        else:
            layout.info(e.file_info.type)

    def display_file(self, e, readme=False):
        if not fnmatch.fnmatch(e.file_info.path.lower(), self.file_wildcard):
            return

        path = e.file_info.path
        fname = os.path.basename(path).lower()
        if not readme and fname == "readme.md":
            return
        self.load_file(e)

        if self.file_error_checkbox and e.valid_loading():
            return

        title = self.get_file_title(e)

        button_layout = st.empty()

        if "currently_opened" not in st.session_state:
            st.session_state["currently_opened"] = None

        def switch_view():
            e.state.view = True
            st.session_state["currently_opened"] = e.file_info.path

        button_layout.button(f"{title}", use_container_width=True, on_click=switch_view)

        # force visibility of readme
        if fname == "readme.md":
            e.state.view = True

        details_layout = st.expander(
            f"{title}",
            expanded=st.session_state["currently_opened"] == e.file_info.path,
        )
        if e.state.view is True:
            button_layout.empty()
            if not e.state.valid and e.state.errors:
                for err in e.errors:
                    details_layout.warning(err)

            col1, col2, col3, col4 = details_layout.columns(4)
            col1.download_button(
                f"Download {os.path.basename(e.file_info.path)}",
                data=open(e.file_info.path, "rb"),
                file_name=os.path.basename(e.file_info.path),
                key="download_" + e.file_info.path,
            )

            if self.git_origin is not None:
                url = self.get_file_edit_link(e)
                col3.markdown(f"[Edit on Gitlab]({url})", unsafe_allow_html=True)

            self.mime_type_information(e, col4, details_layout)
            with details_layout:
                e.view()

    def scan_directories(self, dir_path):
        paths_to_explore = []
        all_paths = []
        self._open_in_jupyterlab_button()
        self._force_rescan_button()

        _st = self.file_selector.expander("File selection tool", expanded=True)
        self.file_wildcard = _st.text_input("File pattern", value=self.file_wildcard)
        self.file_error_checkbox = _st.checkbox("Show only files with errors")

        with st.spinner("Loading directories..."):
            if "scanned_files" not in st.session_state:
                st.session_state["scanned_files"] = {}
                h = self.scanner.scan(dir_path, scan_files=False)
                s_files = st.session_state["scanned_files"]
                s_files["all_paths"] = [d[0] for d in for_each_file(h)]
                s_files["nodes"] = transform_to_subtree(h)
            else:
                s_files = st.session_state["scanned_files"]
            nodes = s_files["nodes"]
            all_paths = s_files["all_paths"]
            _st = self.file_selector.expander("Path selection", expanded=True)
            with _st:
                return_select = tree_select(
                    nodes,
                    expanded=all_paths,
                    expand_disabled=True,
                    checked=all_paths,
                )
                paths_to_explore.clear()
                for c in return_select["checked"]:
                    paths_to_explore.append(c)

        return all_paths, paths_to_explore

    def main(self, dir_path):
        show_logs = self.options.checkbox("Show logs (development)", value=False)
        show_zenodo_publish_button = self.options.checkbox("Show zenodo publish (advanced)", value=False)

        self._zenodo_info()
        self._zenodo_publish(show_zenodo_publish_button)
        self._environment_info()
        if self.git_repository is not None:
            self._git_info()
        if self.git_origin is not None:
            self._gitlab_issues()

        st.markdown(
            """
        <style>
        .css-fxzapv {
          justify-content: left;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )
        st.markdown("---")
        all_paths, selected_paths = self.scan_directories(dir_path)

        if not selected_paths:
            st.markdown("#### Please select a directory on the left panel")
            return

        if "all_found_files" not in st.session_state:
            with st.spinner("Scanning files..."):
                st.session_state["all_found_files"] = self.scan_files([p for p in all_paths])

        all_found_files = st.session_state["all_found_files"]

        if not all_found_files:
            st.markdown(f"#### Nothing in the paths: {selected_paths}")
            return

        self.display_files(all_found_files, selected_paths)

        if show_logs:
            with self.logs.expander("Logs"):
                st.markdown("---")
                for k, v in reversed(st.session_state["logs"]):
                    st.markdown(f"**{k}** -> {type(v).__name__}")
                    st.markdown(v)
            with self.logs.expander("State"):
                st.json(st.session_state, expanded=False)

    def _get_jupyter_link(self):
        try:
            session = os.environ["SESSION_URL"]
            dir_path = os.getcwd()
            rel_path = os.path.relpath(dir_path, self.git_root)
            _link = f"{session}/lab/tree/{rel_path}"
            return _link
        except Exception:
            raise RuntimeError("Not in a renku session")

    def _jupyter_link(self, uri, size):
        _img = f'<a href="{uri}"><img height="{size}" src="data:image/png;base64,{_jupyter_icon}"></a>'
        return _img

    def _write_jupyter_link(self):
        try:
            _link = self._get_jupyter_link()
            im_link = self._jupyter_link(_link, "50em")
            st.markdown(
                f"{im_link} [Edit in Jupyterlab]({_link})",
                unsafe_allow_html=True,
            )
        except Exception as err:
            st.error("Jupyter not accessible")
            st.error(err)

    def display_files(self, found, selected_paths):
        files = for_each_file(found)
        bar = self.progress_layout.progress(0, text="Loading files")

        selected_files = []
        for full_path, f in files:
            if os.path.dirname(full_path) not in selected_paths and full_path not in selected_paths:
                continue
            selected_files.append((full_path, f))

        n_files = len(selected_files)

        for i, (full_path, f) in enumerate(selected_files):
            percent_complete = i * 100 // n_files
            bar.progress(percent_complete + 1, text=f"Loading {full_path}")
            if isinstance(f, File):
                f = FileWrapper(f)
                f.state.set_logger(lambda key, m: self.logger(key, m))
                self.display_file(f)
            else:
                self.display_dir(full_path, f)
        self.progress_layout.empty()

    def display_dir(self, d, content):
        found_files = False
        for k, v in content.items():
            if isinstance(v, File):
                if fnmatch.fnmatch(v.file_info.path.lower(), self.file_wildcard):
                    found_files = True

        if found_files:
            components.html(
                '<div style="'
                "padding-left: .5em;"
                "padding-top: .1em;"
                "padding-bottom: .1em;"
                "border-radius: .5em;"
                "border: 5px solid #c2e8f9;"
                "background-color: #dbeff8;"
                'color:black;"><h3> &#128193; &nbsp;&nbsp;'
                f"{d} </h3></div>"
            )

        for k, v in content.items():
            if not isinstance(v, File):
                continue
            n = os.path.basename(v.file_info.path).lower()
            if n == "readme.md":
                v = FileWrapper(v)
                v.state.set_logger(lambda key, m: self.logger(key, m))
                self.display_file(v, readme=True)

    def _open_in_jupyterlab_button(self):
        with self.jupyter_control.expander("Open in Jupyterlab"):
            self._write_jupyter_link()

    def _environment_info(self):
        with self.env_layout.expander("Environment"):
            table_env = [k for k in os.environ.items()]
            st.dataframe(table_env)

    def _zenodo_publish(self, show=False):
        if not show:
            return
        with self.zenodo_publish_layout.expander("Publish in Zenodo"):
            token = st.text_input("Zenodo token", type="password")
            dry_run = st.checkbox("sandbox", value=True)
            zenodo_metadata = get_study_metadata()
            existing_identifier = False
            if "doi" in zenodo_metadata:
                existing_identifier = zenodo_metadata["doi"]

            col1, col2 = st.columns(2)
            title = "Submit as draft to Zenodo sandbox"
            if not dry_run:
                title = "Submit as draft to Zenodo"
                col2.markdown(
                    "**Not using sandbox will submit to the main "
                    "Zenodo website. Please push content with caution "
                    "as it may result in a permanent entry**"
                )

            submit = col1.button(title, type="primary")
            if submit:
                try:
                    self.zenodo_upload(token, existing_identifier, sandbox=dry_run)
                except Exception as e:
                    self.global_message.error(e)

    def zenodo_upload(self, access_token, existing_identifier, sandbox=True, new_deposition=False):
        import solidipes.scripts.upload as upload

        if self.git_root is not None:
            _dir = self.git_root
        else:
            try:
                _dir = get_solidipes_directory()
            except FileNotFoundError as e:
                self.global_message.error(e)
                return

        metadata = upload.load_and_check_metadata(_dir)
        archive_path, temp_dir = upload.create_archive(_dir)
        deposition_url, bucket_url, web_url = upload.get_cleaned_deposition_infos(
            new_deposition, existing_identifier, access_token, sandbox
        )

        class WebProgressBar:
            def __init__(self, layout, filename, size):
                self.layout = layout
                self.bar = self.layout.progress(0, text="Upload Archive to **Zenodo**")
                self.filename = filename
                self.size = size
                self.uploaded = 0

            def close(self):
                self.layout.empty()

            def update(self, x):
                self.uploaded += x
                percent_complete = self.uploaded * 100 // self.size
                self.bar.progress(
                    percent_complete,
                    text=f"Upload Archive to **Zenodo {percent_complete}%**",
                )

        upload.update_deposition_metadata(deposition_url, metadata, access_token)
        upload.upload_archive(
            bucket_url,
            archive_path,
            access_token,
            progressbar=lambda filename, size: WebProgressBar(self.progress_layout, filename, size),
        )

        self.global_message.info(f"Deposition {'updated' if existing_identifier else 'created'}: {web_url}")
        self.global_message.warning("Please review your deposition and publish it when ready.")

        temp_dir.cleanup()

    def _zenodo_info(self):
        zenodo_metadata = get_study_metadata()

        if "title" in zenodo_metadata:
            self.zenodo_layout.markdown(
                f'# <center>  {zenodo_metadata["title"]} </center>',
                unsafe_allow_html=True,
            )

        if "upload_type" in zenodo_metadata:
            self.zenodo_layout.markdown(
                f'## <center> ({zenodo_metadata["upload_type"]})</center>',
                unsafe_allow_html=True,
            )

        if "creators" in zenodo_metadata:
            with self.zenodo_layout.expander("Authors"):
                for auth in zenodo_metadata["creators"]:
                    text = ""
                    if "name" in auth:
                        text += auth["name"]
                    if "orcid" in auth:
                        text += f', ORCID: {auth["orcid"]}'
                    st.markdown("- " + text)

        # if "description" not in zenodo_metadata:
        #     import markdown
        #     main_readme = os.path.join(self.git_root, "README.md")
        #     zenodo_metadata["description"] = markdown.markdown(
        #         open(main_readme).read()
        #     )
        #     set_study_metadata(zenodo_metadata)

        if "description" in zenodo_metadata:
            with self.zenodo_layout.expander("Description (should be main README.md)"):
                st.markdown(
                    f'{zenodo_metadata["description"]}',
                    unsafe_allow_html=True,
                )

        if "keywords" in zenodo_metadata:
            with self.zenodo_layout.expander("Keywords"):
                for k in zenodo_metadata["keywords"]:
                    st.markdown(f"- {k}")

        with self.zenodo_layout.expander("**Metadata** (Zenodo format)", expanded=False):
            st.markdown("You can edit the metadata below")
            st.markdown(
                "*Description of the Zenodo metadata can be found"
                " [here](https://github.com/zenodo/developers.zenodo.org"
                "/blob/master/source/includes/resources/deposit/"
                "_representation.md#deposit-metadata)*"
            )
            st.markdown("---")
            # Spawn a new Ace editor
            import yaml

            zenodo_metadata = get_study_metadata()
            zenodo_content = yaml.safe_dump(zenodo_metadata)

            self.logger("zenodo_content", zenodo_content)

            content = st_ace(
                value=zenodo_content,
                language="yaml",
                theme="textmate",
                show_gutter=False,
                key="zenodo_metadata_editor",
            )

            self.logger("content", content)
            self.logger("zenodo_content", zenodo_content)

            if content != zenodo_content:
                set_study_metadata(yaml.safe_load(content))
                self.logger("Rewrote zenodo_content", content)
                st.experimental_rerun()

    def _gitlab_issues(self):
        import gitlab

        # self.git_origin has the form "repo_uri/user_name/project_name"
        # repo_uri contains multiple "/"
        if "PROJECT_NAME" not in os.environ:
            split = self.git_origin.split("/")
            project_name = split[-1]
            user_name = split[-2]
            repo_uri = self.git_origin.split(user_name + "/" + project_name)[0]
            os.environ["REPO_URI"] = repo_uri
            os.environ["USER_NAME"] = user_name
            os.environ["PROJECT_NAME"] = project_name
        else:
            project_name = os.environ["PROJECT_NAME"]
            repo_uri_and_user_name = self.git_origin.split("/" + project_name)[0]
            user_name = repo_uri_and_user_name.split("/")[-1]
            repo_uri = repo_uri_and_user_name.split("/" + user_name)[0]
            os.environ["USER_NAME"] = user_name
            os.environ["REPO_URI"] = repo_uri

        project_name = os.environ["PROJECT_NAME"]
        repo_uri = os.environ["REPO_URI"]
        # self.gitlab_issues.write(project_name)
        # self.gitlab_issues.write(repo_uri)

        gl = gitlab.Gitlab(repo_uri)
        try:
            project = gl.projects.get(user_name + "/" + project_name)
        except gitlab.GitlabGetError:
            return
        issues = project.issues.list(get_all=True)

        opened_issues = 0
        for issue in issues:
            if issue.state == "open":
                opened_issues
            if len(issues) == 0:
                return

        self.gitlab_issues.markdown("## Reviews & Issues")
        for issue in issues:
            with self.gitlab_issues.expander(issue.title, expanded=True):
                col1, col2 = st.columns(2)

                col1.image(f'{issue.author["avatar_url"]}')
                col2.markdown(f"### {issue.title}")
                col2.markdown(f'*Author: {issue.author["name"]}*')
                st.markdown(issue.description)
                st.markdown("---")
                st.markdown(f"### :speech_balloon: &nbsp; &nbsp;[**Please reply to the requests**]({issue.web_url})")

                # params = [(k, v) for k, v in issue._attrs.items()
                #           if k != 'description']
                # st.dataframe(params, use_container_width=True)

    def _git_info(self):
        with self.git_control.container():
            changed_files = self.git_get_changed_files()
            if changed_files:
                with st.expander("Modified Files", expanded=True):
                    for p in changed_files:
                        st.markdown(f"- {p}")

                    st.button(
                        "Revert Modifications",
                        type="primary",
                        use_container_width=True,
                        on_click=self.git_revert,
                    )

                    st.button(
                        "Push Modifications",
                        on_click=self.git_push,
                        type="primary",
                        use_container_width=True,
                    )

    def git_get_changed_files(self):
        changed_files = [item.a_path for item in self.git_repository.index.diff(None)]
        return changed_files

    def git_revert(self):
        repo = get_git_repository()
        ret = repo.git.reset("--hard")
        self.logger("git revert", ret)
        self.logger("git revert", type(ret))
        self.logger("git revert return", ret)
        zenodo_metadata = get_study_metadata()
        import yaml

        zenodo_content = yaml.safe_dump(zenodo_metadata)
        st.session_state["zenodo_metadata_editor"] = zenodo_content
        self.logger(
            "st.session_state['zenodo_metadata_editor']",
            st.session_state["zenodo_metadata_editor"],
        )
        st.session_state["rewrote_zenodo_content"] = True
        self.clear_session_state()

    def git_push(self):
        import subprocess

        import git

        try:
            ret = self.git_repository.git.add(f'{" ".join(self.git_get_changed_files())}')
            if ret != "":
                self.global_message.info(ret)

            ret = self.git_repository.git.commit('-m "Automatic update from solidipes interface"')
            if ret != "":
                self.global_message.info(ret)

        except git.GitCommandError as err:
            self.global_message.error(err)
            return

        p = subprocess.Popen(
            "renku dataset update --delete -c --all --no-remote",
            shell=True,
            stdout=subprocess.PIPE,
        )
        p.wait()
        out, err = p.communicate()

        if not p.returncode == 0:
            self.global_message.error("renku update failed")
            self.global_message.error(out.decode())
            self.global_message.error(err.decode())
            return False
        else:
            self.global_message.info(out.decode())

        try:
            origin = self.git_repository.remotes.origin
            origin.push("master")

        except git.GitCommandError as err:
            self.global_message.error(err)
            return

        self.global_message.success("Update repository complete")

        self.clear_session_state()

    def logger(self, key, message):
        if "logs" not in st.session_state:
            st.session_state["logs"] = []
        import inspect

        caller = inspect.stack()[1]
        # filename = caller[1]
        line = caller[2]
        func = caller[3]
        key = func + ":" + str(line) + ": " + key
        st.session_state["logs"].append((key, message))

    def _force_rescan_button(self):
        rescan_button = self.update_buttons.button("Force folder scan", use_container_width=True, type="primary")

        if rescan_button:
            self.clear_session_state()

    def clear_session_state(self):
        keys = [k for k in st.session_state]
        for k in keys:
            del st.session_state[k]


################################################################


def make(dir_path, additional_arguments=""):
    import subprocess

    cmd = f"streamlit run {__file__} {' '.join(additional_arguments)}"
    print(cmd)
    subprocess.call(cmd, shell=True, cwd=dir_path)


################################################################
if __name__ == "__main__":
    report = Report()
    report.main("./")
