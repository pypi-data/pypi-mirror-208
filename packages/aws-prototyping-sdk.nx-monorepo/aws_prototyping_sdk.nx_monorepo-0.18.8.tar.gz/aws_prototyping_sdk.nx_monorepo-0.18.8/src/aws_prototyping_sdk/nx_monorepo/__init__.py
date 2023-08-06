'''
The nx-monorepo package vends a NxMonorepoProject Projen construct that adds [NX](https://nx.dev/getting-started/intro) monorepo support and manages your yarn/npm/pnpm workspaces on your behalf. This construct enables polyglot builds (and inter language build dependencies), build caching, dependency visualization and much, much more.

The PDK itself uses the nx-monorepo project itself and is a good reference for seeing how a complex, polyglot monorepo can be set up.

> **BREAKING CHANGES** (pre-release)
>
> * v0.13.0: `WorkspaceConfig.nxConfig` type `NxConfig => Nx.WorkspaceConfig`, and `overrideProjectTargets` removed in favor of `PDKProject.nx` config to manage Nx project configurations. See [PR 231](https://github.com/aws/aws-prototyping-sdk/pull/231).

To get started simply run the following command in an empty directory:

```bash
npx projen new --from @aws-prototyping-sdk/nx-monorepo
```

This will bootstrap a new Projen monorepo and contain the following in the .projenrc.ts:

```python
import { nx_monorepo } from "aws-prototyping-sdk";

const project = new nx_monorepo.NxMonorepoProject({
  defaultReleaseBranch: "main",
  deps: ["aws-cdk-lib", "constructs", "cdk-nag"],
  devDeps: ["aws-prototyping-sdk"],
  name: "my-package",
});

project.synth();
```

To add new packages to the monorepo, you can simply add them as a child to the monorepo. To demonstrate, lets add a PDK Pipeline TS Project as a child as follows:

```python
import { nx_monorepo } from "aws-prototyping-sdk";

const project = new nx_monorepo.NxMonorepoProject({
  defaultReleaseBranch: "main",
  deps: ["aws-cdk-lib", "constructs", "cdk-nag"],
  devDeps: ["aws-prototyping-sdk"],
  name: "my-package",
});

new PDKPipelineTsProject({
  parent: project,
  outdir: "packages/cicd",
  defaultReleaseBranch: "mainline",
  name: "cicd",
  cdkVersion: "2.1.0"
});

project.synth();
```

Once added, run `npx projen` from the root directory. You will now notice a new TS package has been created under the packages/cicd path.

Now let's add a python project to the monorepo and add an inter-language build dependency.

```python
import { nx_monorepo } from "aws-prototyping-sdk";
import { PDKPipelineTsProject } from "aws-prototyping-sdk/pipeline";
import { PythonProject } from "projen/lib/python";

const project = new nx_monorepo.NxMonorepoProject({
  defaultReleaseBranch: "main",
  deps: ["aws-cdk-lib", "constructs", "cdk-nag"],
  devDeps: ["aws-prototyping-sdk"],
  name: "test",
});

const pipelineProject = new PDKPipelineTsProject({
  parent: project,
  outdir: "packages/cicd",
  defaultReleaseBranch: "mainline",
  name: "cicd",
  cdkVersion: "2.1.0"
});

// Standard Projen projects also work here
const pythonlib = new PythonProject({
  parent: project,
  outdir: "packages/pythonlib",
  authorEmail: "",
  authorName: "",
  moduleName: "pythonlib",
  name: "pythonlib",
  version: "0.0.0"
});

// Pipeline project depends on pythonlib to build first
project.addImplicitDependency(pipelineProject, pythonlib);

project.synth();
```

Run `npx projen` from the root directory. You will now notice a new Python package has been created under packages/pythonlib.

To visualize our dependency graph, run the following command from the root directory: `npx nx graph`.

Now lets test building our project, from the root directory run `npx nx run-many --target=build --nx-bail`. As you can see, the pythonlib was built first followed by the cicd package.

> This is equivalent to running `yarn build`, `pnpm build`, or `npm run build` depending on your node package manager, and similarly `yarn build` also accepts the same [Nx Run-Many options](https://nx.dev/packages/nx/documents/run-many#options) (eg: `yarn build --projects=cicd`).

The NxMonorepoProject also manages your yarn/pnpm workspaces for you and synthesizes these into your package.json pnpm-workspace.yml respectively.

For more information on NX commands, refer to this [documentation](https://nx.dev/using-nx/nx-cli).

### Homogenous Dependencies

As well as adding implicit dependencies, you can add dependencies between projects of the same language in order to have one project consume another project's code.

#### Typescript

Since the `NxMonorepoProject` manages a yarn/npm/pnpm workspace, configuring dependencies between Typescript projects is as straightforward as referencing them in `deps`.

Note that dependencies cannot be added in the same project synthesis (`npx projen`) as when projects are created. This means a two-pass approach is recommended, first to create your new projects, and then to add the dependencies.

For example:

First add your new projects:

```python
new TypeScriptProject({
  parent: monorepo,
  outdir: "packages/a",
  defaultReleaseBranch: "main",
  name: "project-a"
});

new TypeScriptProject({
  parent: monorepo,
  outdir: "packages/b",
  defaultReleaseBranch: "main",
  name: "project-b",
});
```

Synthesise, then you can set up your dependency:

```python
const a = new TypeScriptProject({
  parent: monorepo,
  outdir: "packages/a",
  defaultReleaseBranch: "main",
  name: "project-a"
});

new TypeScriptProject({
  parent: monorepo,
  outdir: "packages/b",
  defaultReleaseBranch: "main",
  name: "project-b",
  // B depends on A
  deps: [a.package.packageName],
});
```

#### Python

##### Poetry (Recommended)

The recommended way to configure dependencies between python projects within your monorepo is to use Poetry. Poetry sets up separate virtual environments per project but also supports local file dependencies. You can use the monorepo's `addPythonPoetryDependency` method:

```python
const a = new PythonProject({
  parent: monorepo,
  outdir: 'packages/a',
  moduleName: 'a',
  name: 'a',
  authorName: 'jack',
  authorEmail: 'me@example.com',
  version: '1.0.0',
  poetry: true,
});

const b = new PythonProject({
  parent: monorepo,
  outdir: 'packages/b',
  moduleName: 'b',
  name: 'b',
  authorName: 'jack',
  authorEmail: 'me@example.com',
  version: '1.0.0',
  poetry: true,
});

// b depends on a
monorepo.addPythonPoetryDependency(b, a);
```

##### Pip

If you are using pip for your python projects, you can set up a dependency using a single shared virtual environment. You can then install packages you wish to depend on into that environment using pip's [Editable Installs](https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs).

You will also need to add an implicit dependency to tell the monorepo the correct build order for your packages.

For example:

```python
const sharedEnv: VenvOptions = {
  envdir: '../../.env',
};

const a = new PythonProject({
  parent: monorepo,
  outdir: 'packages/a',
  moduleName: 'a',
  name: 'a',
  authorName: 'jack',
  authorEmail: 'me@example.com',
  version: '1.0.0',
  venvOptions: sharedEnv,
});

// Install A into the virtual env since it is consumed by B
a.tasks.tryFind('install')!.exec('pip install --editable .');

const b = new PythonProject({
  parent: monorepo,
  outdir: 'packages/b',
  moduleName: 'b',
  name: 'b',
  authorName: 'jack',
  authorEmail: 'me@example.com',
  version: '1.0.0',
  venvOptions: sharedEnv,
  // B depends on A
  deps: [a.moduleName],
});

// Add the implicit dependency so that the monorepo will build A before B
monorepo.addImplicitDependency(b, a);
```

#### Java

The recommended way to configure dependencies between java projects within your monorepo is to use shared maven repositories. The default java project build will already create a distributable in the correct format for a maven repository in its `dist/java` folder, so you can use this as a repository. You can use the monorepo's `addJavaDependency` method:

For example:

```python
const a = new JavaProject({
  parent: monorepo,
  outdir: 'packages/a',
  groupId: 'com.mycompany',
  artifactId: 'a',
  name: 'a',
  version: '1.0.0',
});

const b = new JavaProject({
  parent: monorepo,
  outdir: 'packages/b',
  groupId: 'com.mycompany',
  artifactId: 'b',
  name: 'b',
  version: '1.0.0',
});

// b depends on a
monorepo.addJavaDependency(b, a);
```
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from ._jsii import *

import projen as _projen_04054675
import projen.github as _projen_github_04054675
import projen.github.workflows as _projen_github_workflows_04054675
import projen.java as _projen_java_04054675
import projen.javascript as _projen_javascript_04054675
import projen.python as _projen_python_04054675
import projen.release as _projen_release_04054675
import projen.typescript as _projen_typescript_04054675
from .nx import (
    IInput as _IInput_844dcc6a,
    INxAffectedConfig as _INxAffectedConfig_f6105638,
    IProjectTarget as _IProjectTarget_963c071e,
    IWorkspaceLayout as _IWorkspaceLayout_91f3d180,
    ProjectConfig as _ProjectConfig_a9302870,
    RunManyOptions as _RunManyOptions_ee2ec23f,
)


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/nx-monorepo.MonorepoUpgradeDepsOptions",
    jsii_struct_bases=[],
    name_mapping={"syncpack_config": "syncpackConfig", "task_name": "taskName"},
)
class MonorepoUpgradeDepsOptions:
    def __init__(
        self,
        *,
        syncpack_config: typing.Optional[typing.Union["SyncpackConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        task_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Configuration for Monorepo Upgrade Deps task.

        :param syncpack_config: Syncpack configuration. No merging is performed and as such a complete syncpackConfig is required if supplied. Default: SyncpackConfig.DEFAULT_CONFIG
        :param task_name: Name of the task to create. Default: upgrade-deps
        '''
        if isinstance(syncpack_config, dict):
            syncpack_config = SyncpackConfig(**syncpack_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c1e96ba8c2eed7a2799c05d61a028d1e50d166fd4fda4afd2a90eb0eeecca27)
            check_type(argname="argument syncpack_config", value=syncpack_config, expected_type=type_hints["syncpack_config"])
            check_type(argname="argument task_name", value=task_name, expected_type=type_hints["task_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if syncpack_config is not None:
            self._values["syncpack_config"] = syncpack_config
        if task_name is not None:
            self._values["task_name"] = task_name

    @builtins.property
    def syncpack_config(self) -> typing.Optional["SyncpackConfig"]:
        '''Syncpack configuration.

        No merging is performed and as such a complete syncpackConfig is required if supplied.

        :default: SyncpackConfig.DEFAULT_CONFIG
        '''
        result = self._values.get("syncpack_config")
        return typing.cast(typing.Optional["SyncpackConfig"], result)

    @builtins.property
    def task_name(self) -> typing.Optional[builtins.str]:
        '''Name of the task to create.

        :default: upgrade-deps
        '''
        result = self._values.get("task_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MonorepoUpgradeDepsOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NxMonorepoProject(
    _projen_typescript_04054675.TypeScriptProject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/nx-monorepo.NxMonorepoProject",
):
    '''This project type will bootstrap a NX based monorepo with support for polygot builds, build caching, dependency graph visualization and much more.

    :pjid: nx-monorepo
    '''

    def __init__(
        self,
        *,
        monorepo_upgrade_deps: typing.Optional[builtins.bool] = None,
        monorepo_upgrade_deps_options: typing.Optional[typing.Union[MonorepoUpgradeDepsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        workspace_config: typing.Optional[typing.Union["WorkspaceConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        disable_tsconfig: typing.Optional[builtins.bool] = None,
        disable_tsconfig_dev: typing.Optional[builtins.bool] = None,
        docgen: typing.Optional[builtins.bool] = None,
        docs_directory: typing.Optional[builtins.str] = None,
        entrypoint_types: typing.Optional[builtins.str] = None,
        eslint: typing.Optional[builtins.bool] = None,
        eslint_options: typing.Optional[typing.Union[_projen_javascript_04054675.EslintOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        libdir: typing.Optional[builtins.str] = None,
        projenrc_ts: typing.Optional[builtins.bool] = None,
        projenrc_ts_options: typing.Optional[typing.Union[_projen_typescript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        sample_code: typing.Optional[builtins.bool] = None,
        srcdir: typing.Optional[builtins.str] = None,
        testdir: typing.Optional[builtins.str] = None,
        tsconfig: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        tsconfig_dev: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        tsconfig_dev_file: typing.Optional[builtins.str] = None,
        typescript_version: typing.Optional[builtins.str] = None,
        default_release_branch: builtins.str,
        artifacts_directory: typing.Optional[builtins.str] = None,
        auto_approve_upgrades: typing.Optional[builtins.bool] = None,
        build_workflow: typing.Optional[builtins.bool] = None,
        build_workflow_triggers: typing.Optional[typing.Union[_projen_github_workflows_04054675.Triggers, typing.Dict[builtins.str, typing.Any]]] = None,
        bundler_options: typing.Optional[typing.Union[_projen_javascript_04054675.BundlerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        code_cov: typing.Optional[builtins.bool] = None,
        code_cov_token_secret: typing.Optional[builtins.str] = None,
        copyright_owner: typing.Optional[builtins.str] = None,
        copyright_period: typing.Optional[builtins.str] = None,
        dependabot: typing.Optional[builtins.bool] = None,
        dependabot_options: typing.Optional[typing.Union[_projen_github_04054675.DependabotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        deps_upgrade: typing.Optional[builtins.bool] = None,
        deps_upgrade_options: typing.Optional[typing.Union[_projen_javascript_04054675.UpgradeDependenciesOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        jest: typing.Optional[builtins.bool] = None,
        jest_options: typing.Optional[typing.Union[_projen_javascript_04054675.JestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        mutable_build: typing.Optional[builtins.bool] = None,
        npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        npmignore_enabled: typing.Optional[builtins.bool] = None,
        npm_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        package: typing.Optional[builtins.bool] = None,
        prettier: typing.Optional[builtins.bool] = None,
        prettier_options: typing.Optional[typing.Union[_projen_javascript_04054675.PrettierOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projen_dev_dependency: typing.Optional[builtins.bool] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_js_options: typing.Optional[typing.Union[_projen_javascript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projen_version: typing.Optional[builtins.str] = None,
        pull_request_template: typing.Optional[builtins.bool] = None,
        pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
        release: typing.Optional[builtins.bool] = None,
        release_to_npm: typing.Optional[builtins.bool] = None,
        release_workflow: typing.Optional[builtins.bool] = None,
        workflow_bootstrap_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        workflow_git_identity: typing.Optional[typing.Union[_projen_github_04054675.GitIdentity, typing.Dict[builtins.str, typing.Any]]] = None,
        workflow_node_version: typing.Optional[builtins.str] = None,
        auto_approve_options: typing.Optional[typing.Union[_projen_github_04054675.AutoApproveOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        auto_merge: typing.Optional[builtins.bool] = None,
        auto_merge_options: typing.Optional[typing.Union[_projen_github_04054675.AutoMergeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[typing.Union[_projen_github_04054675.GitHubOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[typing.Union[_projen_github_04054675.MergifyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        project_type: typing.Optional[_projen_04054675.ProjectType] = None,
        projen_credentials: typing.Optional[_projen_github_04054675.GithubCredentials] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        readme: typing.Optional[typing.Union[_projen_04054675.SampleReadmeProps, typing.Dict[builtins.str, typing.Any]]] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[typing.Union[_projen_github_04054675.StaleOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        vscode: typing.Optional[builtins.bool] = None,
        allow_library_dependencies: typing.Optional[builtins.bool] = None,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        author_organization: typing.Optional[builtins.bool] = None,
        author_url: typing.Optional[builtins.str] = None,
        auto_detect_bin: typing.Optional[builtins.bool] = None,
        bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        bugs_email: typing.Optional[builtins.str] = None,
        bugs_url: typing.Optional[builtins.str] = None,
        bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        code_artifact_options: typing.Optional[typing.Union[_projen_javascript_04054675.CodeArtifactOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        entrypoint: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        license: typing.Optional[builtins.str] = None,
        licensed: typing.Optional[builtins.bool] = None,
        max_node_version: typing.Optional[builtins.str] = None,
        min_node_version: typing.Optional[builtins.str] = None,
        npm_access: typing.Optional[_projen_javascript_04054675.NpmAccess] = None,
        npm_registry: typing.Optional[builtins.str] = None,
        npm_registry_url: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        package_manager: typing.Optional[_projen_javascript_04054675.NodePackageManager] = None,
        package_name: typing.Optional[builtins.str] = None,
        peer_dependency_options: typing.Optional[typing.Union[_projen_javascript_04054675.PeerDependencyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        pnpm_version: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
        repository_directory: typing.Optional[builtins.str] = None,
        scoped_packages_options: typing.Optional[typing.Sequence[typing.Union[_projen_javascript_04054675.ScopedPackagesOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        stability: typing.Optional[builtins.str] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        min_major_version: typing.Optional[jsii.Number] = None,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        publish_dry_run: typing.Optional[builtins.bool] = None,
        publish_tasks: typing.Optional[builtins.bool] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, typing.Union[_projen_release_04054675.BranchOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_failure_issue: typing.Optional[builtins.bool] = None,
        release_failure_issue_label: typing.Optional[builtins.str] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_tag_prefix: typing.Optional[builtins.str] = None,
        release_trigger: typing.Optional[_projen_release_04054675.ReleaseTrigger] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        name: builtins.str,
        commit_generated: typing.Optional[builtins.bool] = None,
        git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_projen_04054675.Project] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param monorepo_upgrade_deps: Whether to include an upgrade-deps task at the root of the monorepo which will upgrade all dependencies. Default: true
        :param monorepo_upgrade_deps_options: Monorepo Upgrade Deps options. This is only used if monorepoUpgradeDeps is true. Default: undefined
        :param workspace_config: Configuration for workspace.
        :param disable_tsconfig: (experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler). Default: false
        :param disable_tsconfig_dev: (experimental) Do not generate a ``tsconfig.dev.json`` file. Default: false
        :param docgen: (experimental) Docgen by Typedoc. Default: false
        :param docs_directory: (experimental) Docs directory. Default: "docs"
        :param entrypoint_types: (experimental) The .d.ts file that includes the type declarations for this module. Default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)
        :param eslint: (experimental) Setup eslint. Default: true
        :param eslint_options: (experimental) Eslint options. Default: - opinionated default options
        :param libdir: (experimental) Typescript artifacts output directory. Default: "lib"
        :param projenrc_ts: (experimental) Use TypeScript for your projenrc file (``.projenrc.ts``). Default: false
        :param projenrc_ts_options: (experimental) Options for .projenrc.ts.
        :param sample_code: (experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there. Default: true
        :param srcdir: (experimental) Typescript sources directory. Default: "src"
        :param testdir: (experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``. If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``), then tests are going to be compiled into ``lib/`` and executed as javascript. If the test directory is outside of ``src``, then we configure jest to compile the code in-memory. Default: "test"
        :param tsconfig: (experimental) Custom TSConfig. Default: - default options
        :param tsconfig_dev: (experimental) Custom tsconfig options for the development tsconfig.json file (used for testing). Default: - use the production tsconfig options
        :param tsconfig_dev_file: (experimental) The name of the development tsconfig.json file. Default: "tsconfig.dev.json"
        :param typescript_version: (experimental) TypeScript version to use. NOTE: Typescript is not semantically versioned and should remain on the same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``). Default: "latest"
        :param default_release_branch: (experimental) The name of the main release branch. Default: "main"
        :param artifacts_directory: (experimental) A directory which will contain build artifacts. Default: "dist"
        :param auto_approve_upgrades: (experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: - true
        :param build_workflow: (experimental) Define a GitHub workflow for building PRs. Default: - true if not a subproject
        :param build_workflow_triggers: (experimental) Build workflow triggers. Default: "{ pullRequest: {}, workflowDispatch: {} }"
        :param bundler_options: (experimental) Options for ``Bundler``.
        :param code_cov: (experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v3 A secret is required for private repos. Configured with @codeCovTokenSecret. Default: false
        :param code_cov_token_secret: (experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories. Default: - if this option is not specified, only public repositories are supported
        :param copyright_owner: (experimental) License copyright owner. Default: - defaults to the value of authorName or "" if ``authorName`` is undefined.
        :param copyright_period: (experimental) The copyright years to put in the LICENSE file. Default: - current year
        :param dependabot: (experimental) Use dependabot to handle dependency upgrades. Cannot be used in conjunction with ``depsUpgrade``. Default: false
        :param dependabot_options: (experimental) Options for dependabot. Default: - default options
        :param deps_upgrade: (experimental) Use github workflows to handle dependency upgrades. Cannot be used in conjunction with ``dependabot``. Default: true
        :param deps_upgrade_options: (experimental) Options for ``UpgradeDependencies``. Default: - default options
        :param gitignore: (experimental) Additional entries to .gitignore.
        :param jest: (experimental) Setup jest unit tests. Default: true
        :param jest_options: (experimental) Jest options. Default: - default options
        :param mutable_build: (experimental) Automatically update files modified during builds to pull-request branches. This means that any files synthesized by projen or e.g. test snapshots will always be up-to-date before a PR is merged. Implies that PR builds do not have anti-tamper checks. Default: true
        :param npmignore: (deprecated) Additional entries to .npmignore.
        :param npmignore_enabled: (experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs. Default: true
        :param npm_ignore_options: (experimental) Configuration options for .npmignore file.
        :param package: (experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``). Default: true
        :param prettier: (experimental) Setup prettier. Default: false
        :param prettier_options: (experimental) Prettier options. Default: - default options
        :param projen_dev_dependency: (experimental) Indicates of "projen" should be installed as a devDependency. Default: true
        :param projenrc_js: (experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation. Default: - true if projenrcJson is false
        :param projenrc_js_options: (experimental) Options for .projenrc.js. Default: - default options
        :param projen_version: (experimental) Version of projen to install. Default: - Defaults to the latest version.
        :param pull_request_template: (experimental) Include a GitHub pull request template. Default: true
        :param pull_request_template_contents: (experimental) The contents of the pull request template. Default: - default content
        :param release: (experimental) Add release management to this project. Default: - true (false for subprojects)
        :param release_to_npm: (experimental) Automatically release to npm when new versions are introduced. Default: false
        :param release_workflow: (deprecated) DEPRECATED: renamed to ``release``. Default: - true if not a subproject
        :param workflow_bootstrap_steps: (experimental) Workflow steps to use in order to bootstrap this repo. Default: "yarn install --frozen-lockfile && yarn projen"
        :param workflow_git_identity: (experimental) The git identity to use in workflows. Default: - GitHub Actions
        :param workflow_node_version: (experimental) The node version to use in GitHub workflows. Default: - same as ``minNodeVersion``
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge: (experimental) Enable automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: true
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` or ``autoMerge`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: - true, but false for subprojects
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_credentials: (experimental) Choose a method of providing GitHub API access for projen workflows. Default: - use a personal access token named PROJEN_GITHUB_TOKEN
        :param projen_token_secret: (deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: false
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param allow_library_dependencies: (experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``. This is normally only allowed for libraries. For apps, there's no meaning for specifying these. Default: true
        :param author_email: (experimental) Author's e-mail.
        :param author_name: (experimental) Author's name.
        :param author_organization: (experimental) Is the author an organization.
        :param author_url: (experimental) Author's URL / Website.
        :param auto_detect_bin: (experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section. Default: true
        :param bin: (experimental) Binary programs vended with your module. You can use this option to add/customize how binaries are represented in your ``package.json``, but unless ``autoDetectBin`` is ``false``, every executable file under ``bin`` will automatically be added to this section.
        :param bugs_email: (experimental) The email address to which issues should be reported.
        :param bugs_url: (experimental) The url to your project's issue tracker.
        :param bundled_deps: (experimental) List of dependencies to bundle into this module. These modules will be added both to the ``dependencies`` section and ``bundledDependencies`` section of your ``package.json``. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include.
        :param code_artifact_options: (experimental) Options for npm packages using AWS CodeArtifact. This is required if publishing packages to, or installing scoped packages from AWS CodeArtifact Default: - undefined
        :param deps: (experimental) Runtime dependencies of this module. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param description: (experimental) The description is just a string that helps people understand the purpose of the package. It can be used when searching for packages in a package manager as well. See https://classic.yarnpkg.com/en/docs/package-json/#toc-description
        :param dev_deps: (experimental) Build dependencies for this module. These dependencies will only be available in your build environment but will not be fetched when this module is consumed. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param entrypoint: (experimental) Module entrypoint (``main`` in ``package.json``). Set to an empty string to not include ``main`` in your package.json Default: "lib/index.js"
        :param homepage: (experimental) Package's Homepage / Website.
        :param keywords: (experimental) Keywords to include in ``package.json``.
        :param license: (experimental) License's SPDX identifier. See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses. Use the ``licensed`` option if you want to no license to be specified. Default: "Apache-2.0"
        :param licensed: (experimental) Indicates if a license should be added. Default: true
        :param max_node_version: (experimental) Minimum node.js version to require via ``engines`` (inclusive). Default: - no max
        :param min_node_version: (experimental) Minimum Node.js version to require via package.json ``engines`` (inclusive). Default: - no "engines" specified
        :param npm_access: (experimental) Access level of the npm package. Default: - for scoped packages (e.g. ``foo@bar``), the default is ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is ``NpmAccess.PUBLIC``.
        :param npm_registry: (deprecated) The host name of the npm registry to publish to. Cannot be set together with ``npmRegistryUrl``.
        :param npm_registry_url: (experimental) The base URL of the npm package registry. Must be a URL (e.g. start with "https://" or "http://") Default: "https://registry.npmjs.org"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: "NPM_TOKEN"
        :param package_manager: (experimental) The Node Package Manager used to execute scripts. Default: NodePackageManager.YARN
        :param package_name: (experimental) The "name" in package.json. Default: - defaults to project name
        :param peer_dependency_options: (experimental) Options for ``peerDeps``.
        :param peer_deps: (experimental) Peer dependencies for this module. Dependencies listed here are required to be installed (and satisfied) by the *consumer* of this library. Using peer dependencies allows you to ensure that only a single module of a certain library exists in the ``node_modules`` tree of your consumers. Note that prior to npm@7, peer dependencies are *not* automatically installed, which means that adding peer dependencies to a library will be a breaking change for your customers. Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is enabled by default), projen will automatically add a dev dependency with a pinned version for each peer dependency. This will ensure that you build & test your module against the lowest peer version required. Default: []
        :param pnpm_version: (experimental) The version of PNPM to use if using PNPM as a package manager. Default: "7"
        :param repository: (experimental) The repository is the location where the actual code for your package lives. See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository
        :param repository_directory: (experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.
        :param scoped_packages_options: (experimental) Options for privately hosted scoped packages. Default: - fetch all scoped packages from the public npm registry
        :param scripts: (deprecated) npm scripts to include. If a script has the same name as a standard script, the standard script will be overwritten. Also adds the script as a task. Default: {}
        :param stability: (experimental) Package's Stability.
        :param jsii_release_version: (experimental) Version requirement of ``publib`` which is used to publish modules to npm. Default: "latest"
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param min_major_version: (experimental) Minimal Major version to release. This can be useful to set to 1, as breaking changes before the 1.x major release are not incrementing the major version number. Can not be set together with ``majorVersion``. Default: - No minimum version is being enforced
        :param npm_dist_tag: (experimental) The npmDistTag to use when publishing from the default branch. To set the npm dist-tag for release branches, set the ``npmDistTag`` property for each branch. Default: "latest"
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param publish_dry_run: (experimental) Instead of actually publishing to package managers, just print the publishing command. Default: false
        :param publish_tasks: (experimental) Define publishing tasks that can be executed manually as well as workflows. Normally, publishing only happens within automated workflows. Enable this in order to create a publishing task for each publishing activity. Default: false
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_failure_issue: (experimental) Create a github issue on every failed publishing task. Default: false
        :param release_failure_issue_label: (experimental) The label to apply to issues indicating publish failures. Only applies if ``releaseFailureIssue`` is true. Default: "failed-release"
        :param release_schedule: (deprecated) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_tag_prefix: (experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers. Note: this prefix is used to detect the latest tagged version when bumping, so if you change this on a project with an existing version history, you may need to manually tag your latest release with the new prefix. Default: "v"
        :param release_trigger: (experimental) The release trigger to use. Default: - Continuous releases (``ReleaseTrigger.continuous()``)
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "Release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param versionrc_options: (experimental) Custom configuration used when creating changelog with standard-version package. Given values either append to default configuration or overwrite values in it. Default: - standard configuration applicable for GitHub repositories
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param workflow_runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param commit_generated: (experimental) Whether to commit the managed files by default. Default: true
        :param git_ignore_options: (experimental) Configuration options for .gitignore file.
        :param git_options: (experimental) Configuration options for git.
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options
        '''
        options = NxMonorepoProjectOptions(
            monorepo_upgrade_deps=monorepo_upgrade_deps,
            monorepo_upgrade_deps_options=monorepo_upgrade_deps_options,
            workspace_config=workspace_config,
            disable_tsconfig=disable_tsconfig,
            disable_tsconfig_dev=disable_tsconfig_dev,
            docgen=docgen,
            docs_directory=docs_directory,
            entrypoint_types=entrypoint_types,
            eslint=eslint,
            eslint_options=eslint_options,
            libdir=libdir,
            projenrc_ts=projenrc_ts,
            projenrc_ts_options=projenrc_ts_options,
            sample_code=sample_code,
            srcdir=srcdir,
            testdir=testdir,
            tsconfig=tsconfig,
            tsconfig_dev=tsconfig_dev,
            tsconfig_dev_file=tsconfig_dev_file,
            typescript_version=typescript_version,
            default_release_branch=default_release_branch,
            artifacts_directory=artifacts_directory,
            auto_approve_upgrades=auto_approve_upgrades,
            build_workflow=build_workflow,
            build_workflow_triggers=build_workflow_triggers,
            bundler_options=bundler_options,
            code_cov=code_cov,
            code_cov_token_secret=code_cov_token_secret,
            copyright_owner=copyright_owner,
            copyright_period=copyright_period,
            dependabot=dependabot,
            dependabot_options=dependabot_options,
            deps_upgrade=deps_upgrade,
            deps_upgrade_options=deps_upgrade_options,
            gitignore=gitignore,
            jest=jest,
            jest_options=jest_options,
            mutable_build=mutable_build,
            npmignore=npmignore,
            npmignore_enabled=npmignore_enabled,
            npm_ignore_options=npm_ignore_options,
            package=package,
            prettier=prettier,
            prettier_options=prettier_options,
            projen_dev_dependency=projen_dev_dependency,
            projenrc_js=projenrc_js,
            projenrc_js_options=projenrc_js_options,
            projen_version=projen_version,
            pull_request_template=pull_request_template,
            pull_request_template_contents=pull_request_template_contents,
            release=release,
            release_to_npm=release_to_npm,
            release_workflow=release_workflow,
            workflow_bootstrap_steps=workflow_bootstrap_steps,
            workflow_git_identity=workflow_git_identity,
            workflow_node_version=workflow_node_version,
            auto_approve_options=auto_approve_options,
            auto_merge=auto_merge,
            auto_merge_options=auto_merge_options,
            clobber=clobber,
            dev_container=dev_container,
            github=github,
            github_options=github_options,
            gitpod=gitpod,
            mergify=mergify,
            mergify_options=mergify_options,
            project_type=project_type,
            projen_credentials=projen_credentials,
            projen_token_secret=projen_token_secret,
            readme=readme,
            stale=stale,
            stale_options=stale_options,
            vscode=vscode,
            allow_library_dependencies=allow_library_dependencies,
            author_email=author_email,
            author_name=author_name,
            author_organization=author_organization,
            author_url=author_url,
            auto_detect_bin=auto_detect_bin,
            bin=bin,
            bugs_email=bugs_email,
            bugs_url=bugs_url,
            bundled_deps=bundled_deps,
            code_artifact_options=code_artifact_options,
            deps=deps,
            description=description,
            dev_deps=dev_deps,
            entrypoint=entrypoint,
            homepage=homepage,
            keywords=keywords,
            license=license,
            licensed=licensed,
            max_node_version=max_node_version,
            min_node_version=min_node_version,
            npm_access=npm_access,
            npm_registry=npm_registry,
            npm_registry_url=npm_registry_url,
            npm_token_secret=npm_token_secret,
            package_manager=package_manager,
            package_name=package_name,
            peer_dependency_options=peer_dependency_options,
            peer_deps=peer_deps,
            pnpm_version=pnpm_version,
            repository=repository,
            repository_directory=repository_directory,
            scoped_packages_options=scoped_packages_options,
            scripts=scripts,
            stability=stability,
            jsii_release_version=jsii_release_version,
            major_version=major_version,
            min_major_version=min_major_version,
            npm_dist_tag=npm_dist_tag,
            post_build_steps=post_build_steps,
            prerelease=prerelease,
            publish_dry_run=publish_dry_run,
            publish_tasks=publish_tasks,
            release_branches=release_branches,
            release_every_commit=release_every_commit,
            release_failure_issue=release_failure_issue,
            release_failure_issue_label=release_failure_issue_label,
            release_schedule=release_schedule,
            release_tag_prefix=release_tag_prefix,
            release_trigger=release_trigger,
            release_workflow_name=release_workflow_name,
            release_workflow_setup_steps=release_workflow_setup_steps,
            versionrc_options=versionrc_options,
            workflow_container_image=workflow_container_image,
            workflow_runs_on=workflow_runs_on,
            name=name,
            commit_generated=commit_generated,
            git_ignore_options=git_ignore_options,
            git_options=git_options,
            logging=logging,
            outdir=outdir,
            parent=parent,
            projen_command=projen_command,
            projenrc_json=projenrc_json,
            projenrc_json_options=projenrc_json_options,
            renovatebot=renovatebot,
            renovatebot_options=renovatebot_options,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="addImplicitDependency")
    def add_implicit_dependency(
        self,
        dependent: _projen_04054675.Project,
        dependee: typing.Union[builtins.str, _projen_04054675.Project],
    ) -> None:
        '''Create an implicit dependency between two Projects.

        This is typically
        used in polygot repos where a Typescript project wants a build dependency
        on a Python project as an example.

        :param dependent: project you want to have the dependency.
        :param dependee: project you wish to depend on.

        :throws: error if this is called on a dependent which does not have a NXProject component attached.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b738e62875428e4cd471aea732c48cddb94f8be4d9c7a17543f94980301f414f)
            check_type(argname="argument dependent", value=dependent, expected_type=type_hints["dependent"])
            check_type(argname="argument dependee", value=dependee, expected_type=type_hints["dependee"])
        return typing.cast(None, jsii.invoke(self, "addImplicitDependency", [dependent, dependee]))

    @jsii.member(jsii_name="addJavaDependency")
    def add_java_dependency(
        self,
        dependent: _projen_java_04054675.JavaProject,
        dependee: _projen_java_04054675.JavaProject,
    ) -> None:
        '''Adds a dependency between two Java Projects in the monorepo.

        :param dependent: project you want to have the dependency.
        :param dependee: project you wish to depend on.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__469636d8b7ed326548f3fc664c77053d0ee24f82f5f5da9f9451853745100a99)
            check_type(argname="argument dependent", value=dependent, expected_type=type_hints["dependent"])
            check_type(argname="argument dependee", value=dependee, expected_type=type_hints["dependee"])
        return typing.cast(None, jsii.invoke(self, "addJavaDependency", [dependent, dependee]))

    @jsii.member(jsii_name="addNxRunManyTask")
    def add_nx_run_many_task(
        self,
        name: builtins.str,
        *,
        target: builtins.str,
        configuration: typing.Optional[builtins.str] = None,
        exclude: typing.Optional[builtins.str] = None,
        ignore_cycles: typing.Optional[builtins.bool] = None,
        no_bail: typing.Optional[builtins.bool] = None,
        output_style: typing.Optional[builtins.str] = None,
        parallel: typing.Optional[jsii.Number] = None,
        projects: typing.Optional[typing.Sequence[builtins.str]] = None,
        runner: typing.Optional[builtins.str] = None,
        skip_cache: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
    ) -> _projen_04054675.Task:
        '''Add project task that executes ``npx nx run-many ...`` style command.

        :param name: -
        :param target: Task to run for affected projects.
        :param configuration: This is the configuration to use when performing tasks on projects.
        :param exclude: Exclude certain projects from being processed.
        :param ignore_cycles: Ignore cycles in the task graph.
        :param no_bail: Do not stop command execution after the first failed task.
        :param output_style: Defines how Nx emits outputs tasks logs. Default: "stream"
        :param parallel: Max number of parallel processes. Default: 3
        :param projects: Project to run as list project names and/or patterns.
        :param runner: This is the name of the tasks runner configuration in nx.json.
        :param skip_cache: Rerun the tasks even when the results are available in the cache.
        :param verbose: Prints additional information about the commands (e.g. stack traces).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cde40306266f76eabf18157fb7e689332894a985e0d906a86e5ca1d108712f4c)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        options = _RunManyOptions_ee2ec23f(
            target=target,
            configuration=configuration,
            exclude=exclude,
            ignore_cycles=ignore_cycles,
            no_bail=no_bail,
            output_style=output_style,
            parallel=parallel,
            projects=projects,
            runner=runner,
            skip_cache=skip_cache,
            verbose=verbose,
        )

        return typing.cast(_projen_04054675.Task, jsii.invoke(self, "addNxRunManyTask", [name, options]))

    @jsii.member(jsii_name="addPythonPoetryDependency")
    def add_python_poetry_dependency(
        self,
        dependent: _projen_python_04054675.PythonProject,
        dependee: _projen_python_04054675.PythonProject,
    ) -> None:
        '''Adds a dependency between two Python Projects in the monorepo.

        The dependent must have Poetry enabled.

        :param dependent: project you want to have the dependency (must be a Poetry Python Project).
        :param dependee: project you wish to depend on.

        :throws: error if the dependent does not have Poetry enabled
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cc271f5bd784e939a1bce2dbc71bf305a7412e0a56f89da5585d6a59adc0e1d)
            check_type(argname="argument dependent", value=dependent, expected_type=type_hints["dependent"])
            check_type(argname="argument dependee", value=dependee, expected_type=type_hints["dependee"])
        return typing.cast(None, jsii.invoke(self, "addPythonPoetryDependency", [dependent, dependee]))

    @jsii.member(jsii_name="addWorkspacePackages")
    def add_workspace_packages(self, *package_globs: builtins.str) -> None:
        '''Add one or more additional package globs to the workspace.

        :param package_globs: paths to the package to include in the workspace (for example packages/my-package).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__723fb65cfda0224919fa6541c686df09d634e2efdcd517f780356d3eff380d51)
            check_type(argname="argument package_globs", value=package_globs, expected_type=typing.Tuple[type_hints["package_globs"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(None, jsii.invoke(self, "addWorkspacePackages", [*package_globs]))

    @jsii.member(jsii_name="composeNxRunManyCommand")
    def compose_nx_run_many_command(
        self,
        *,
        target: builtins.str,
        configuration: typing.Optional[builtins.str] = None,
        exclude: typing.Optional[builtins.str] = None,
        ignore_cycles: typing.Optional[builtins.bool] = None,
        no_bail: typing.Optional[builtins.bool] = None,
        output_style: typing.Optional[builtins.str] = None,
        parallel: typing.Optional[jsii.Number] = None,
        projects: typing.Optional[typing.Sequence[builtins.str]] = None,
        runner: typing.Optional[builtins.str] = None,
        skip_cache: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
    ) -> typing.List[builtins.str]:
        '''Helper to format ``npx nx run-many ...`` style command.

        :param target: Task to run for affected projects.
        :param configuration: This is the configuration to use when performing tasks on projects.
        :param exclude: Exclude certain projects from being processed.
        :param ignore_cycles: Ignore cycles in the task graph.
        :param no_bail: Do not stop command execution after the first failed task.
        :param output_style: Defines how Nx emits outputs tasks logs. Default: "stream"
        :param parallel: Max number of parallel processes. Default: 3
        :param projects: Project to run as list project names and/or patterns.
        :param runner: This is the name of the tasks runner configuration in nx.json.
        :param skip_cache: Rerun the tasks even when the results are available in the cache.
        :param verbose: Prints additional information about the commands (e.g. stack traces).
        '''
        options = _RunManyOptions_ee2ec23f(
            target=target,
            configuration=configuration,
            exclude=exclude,
            ignore_cycles=ignore_cycles,
            no_bail=no_bail,
            output_style=output_style,
            parallel=parallel,
            projects=projects,
            runner=runner,
            skip_cache=skip_cache,
            verbose=verbose,
        )

        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "composeNxRunManyCommand", [options]))

    @jsii.member(jsii_name="execNxRunManyCommand")
    def exec_nx_run_many_command(
        self,
        *,
        target: builtins.str,
        configuration: typing.Optional[builtins.str] = None,
        exclude: typing.Optional[builtins.str] = None,
        ignore_cycles: typing.Optional[builtins.bool] = None,
        no_bail: typing.Optional[builtins.bool] = None,
        output_style: typing.Optional[builtins.str] = None,
        parallel: typing.Optional[jsii.Number] = None,
        projects: typing.Optional[typing.Sequence[builtins.str]] = None,
        runner: typing.Optional[builtins.str] = None,
        skip_cache: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
    ) -> builtins.str:
        '''Helper to format ``npx nx run-many ...`` style command execution in package manager.

        :param target: Task to run for affected projects.
        :param configuration: This is the configuration to use when performing tasks on projects.
        :param exclude: Exclude certain projects from being processed.
        :param ignore_cycles: Ignore cycles in the task graph.
        :param no_bail: Do not stop command execution after the first failed task.
        :param output_style: Defines how Nx emits outputs tasks logs. Default: "stream"
        :param parallel: Max number of parallel processes. Default: 3
        :param projects: Project to run as list project names and/or patterns.
        :param runner: This is the name of the tasks runner configuration in nx.json.
        :param skip_cache: Rerun the tasks even when the results are available in the cache.
        :param verbose: Prints additional information about the commands (e.g. stack traces).
        '''
        options = _RunManyOptions_ee2ec23f(
            target=target,
            configuration=configuration,
            exclude=exclude,
            ignore_cycles=ignore_cycles,
            no_bail=no_bail,
            output_style=output_style,
            parallel=parallel,
            projects=projects,
            runner=runner,
            skip_cache=skip_cache,
            verbose=verbose,
        )

        return typing.cast(builtins.str, jsii.invoke(self, "execNxRunManyCommand", [options]))

    @jsii.member(jsii_name="linkLocalWorkspaceBins")
    def _link_local_workspace_bins(self) -> None:
        '''Create symbolic links to all local workspace bins.

        This enables the usage of bins the same
        way as consumers of the packages have when installing from the registry.
        '''
        return typing.cast(None, jsii.invoke(self, "linkLocalWorkspaceBins", []))

    @jsii.member(jsii_name="preSynthesize")
    def pre_synthesize(self) -> None:
        '''Called before all components are synthesized.'''
        return typing.cast(None, jsii.invoke(self, "preSynthesize", []))

    @jsii.member(jsii_name="synth")
    def synth(self) -> None:
        '''Synthesize all project files into ``outdir``.

        1. Call "this.preSynthesize()"
        2. Delete all generated files
        3. Synthesize all sub-projects
        4. Synthesize all components of this project
        5. Call "postSynthesize()" for all components of this project
        6. Call "this.postSynthesize()"

        :inheritDoc: true
        '''
        return typing.cast(None, jsii.invoke(self, "synth", []))

    @builtins.property
    @jsii.member(jsii_name="nx")
    def nx(self) -> "NxWorkspace":
        return typing.cast("NxWorkspace", jsii.get(self, "nx"))

    @builtins.property
    @jsii.member(jsii_name="sortedSubProjects")
    def sorted_sub_projects(self) -> typing.List[_projen_04054675.Project]:
        '''Get consistently sorted list of subprojects.'''
        return typing.cast(typing.List[_projen_04054675.Project], jsii.get(self, "sortedSubProjects"))


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/nx-monorepo.NxMonorepoProjectOptions",
    jsii_struct_bases=[_projen_typescript_04054675.TypeScriptProjectOptions],
    name_mapping={
        "name": "name",
        "commit_generated": "commitGenerated",
        "git_ignore_options": "gitIgnoreOptions",
        "git_options": "gitOptions",
        "logging": "logging",
        "outdir": "outdir",
        "parent": "parent",
        "projen_command": "projenCommand",
        "projenrc_json": "projenrcJson",
        "projenrc_json_options": "projenrcJsonOptions",
        "renovatebot": "renovatebot",
        "renovatebot_options": "renovatebotOptions",
        "auto_approve_options": "autoApproveOptions",
        "auto_merge": "autoMerge",
        "auto_merge_options": "autoMergeOptions",
        "clobber": "clobber",
        "dev_container": "devContainer",
        "github": "github",
        "github_options": "githubOptions",
        "gitpod": "gitpod",
        "mergify": "mergify",
        "mergify_options": "mergifyOptions",
        "project_type": "projectType",
        "projen_credentials": "projenCredentials",
        "projen_token_secret": "projenTokenSecret",
        "readme": "readme",
        "stale": "stale",
        "stale_options": "staleOptions",
        "vscode": "vscode",
        "allow_library_dependencies": "allowLibraryDependencies",
        "author_email": "authorEmail",
        "author_name": "authorName",
        "author_organization": "authorOrganization",
        "author_url": "authorUrl",
        "auto_detect_bin": "autoDetectBin",
        "bin": "bin",
        "bugs_email": "bugsEmail",
        "bugs_url": "bugsUrl",
        "bundled_deps": "bundledDeps",
        "code_artifact_options": "codeArtifactOptions",
        "deps": "deps",
        "description": "description",
        "dev_deps": "devDeps",
        "entrypoint": "entrypoint",
        "homepage": "homepage",
        "keywords": "keywords",
        "license": "license",
        "licensed": "licensed",
        "max_node_version": "maxNodeVersion",
        "min_node_version": "minNodeVersion",
        "npm_access": "npmAccess",
        "npm_registry": "npmRegistry",
        "npm_registry_url": "npmRegistryUrl",
        "npm_token_secret": "npmTokenSecret",
        "package_manager": "packageManager",
        "package_name": "packageName",
        "peer_dependency_options": "peerDependencyOptions",
        "peer_deps": "peerDeps",
        "pnpm_version": "pnpmVersion",
        "repository": "repository",
        "repository_directory": "repositoryDirectory",
        "scoped_packages_options": "scopedPackagesOptions",
        "scripts": "scripts",
        "stability": "stability",
        "jsii_release_version": "jsiiReleaseVersion",
        "major_version": "majorVersion",
        "min_major_version": "minMajorVersion",
        "npm_dist_tag": "npmDistTag",
        "post_build_steps": "postBuildSteps",
        "prerelease": "prerelease",
        "publish_dry_run": "publishDryRun",
        "publish_tasks": "publishTasks",
        "release_branches": "releaseBranches",
        "release_every_commit": "releaseEveryCommit",
        "release_failure_issue": "releaseFailureIssue",
        "release_failure_issue_label": "releaseFailureIssueLabel",
        "release_schedule": "releaseSchedule",
        "release_tag_prefix": "releaseTagPrefix",
        "release_trigger": "releaseTrigger",
        "release_workflow_name": "releaseWorkflowName",
        "release_workflow_setup_steps": "releaseWorkflowSetupSteps",
        "versionrc_options": "versionrcOptions",
        "workflow_container_image": "workflowContainerImage",
        "workflow_runs_on": "workflowRunsOn",
        "default_release_branch": "defaultReleaseBranch",
        "artifacts_directory": "artifactsDirectory",
        "auto_approve_upgrades": "autoApproveUpgrades",
        "build_workflow": "buildWorkflow",
        "build_workflow_triggers": "buildWorkflowTriggers",
        "bundler_options": "bundlerOptions",
        "code_cov": "codeCov",
        "code_cov_token_secret": "codeCovTokenSecret",
        "copyright_owner": "copyrightOwner",
        "copyright_period": "copyrightPeriod",
        "dependabot": "dependabot",
        "dependabot_options": "dependabotOptions",
        "deps_upgrade": "depsUpgrade",
        "deps_upgrade_options": "depsUpgradeOptions",
        "gitignore": "gitignore",
        "jest": "jest",
        "jest_options": "jestOptions",
        "mutable_build": "mutableBuild",
        "npmignore": "npmignore",
        "npmignore_enabled": "npmignoreEnabled",
        "npm_ignore_options": "npmIgnoreOptions",
        "package": "package",
        "prettier": "prettier",
        "prettier_options": "prettierOptions",
        "projen_dev_dependency": "projenDevDependency",
        "projenrc_js": "projenrcJs",
        "projenrc_js_options": "projenrcJsOptions",
        "projen_version": "projenVersion",
        "pull_request_template": "pullRequestTemplate",
        "pull_request_template_contents": "pullRequestTemplateContents",
        "release": "release",
        "release_to_npm": "releaseToNpm",
        "release_workflow": "releaseWorkflow",
        "workflow_bootstrap_steps": "workflowBootstrapSteps",
        "workflow_git_identity": "workflowGitIdentity",
        "workflow_node_version": "workflowNodeVersion",
        "disable_tsconfig": "disableTsconfig",
        "disable_tsconfig_dev": "disableTsconfigDev",
        "docgen": "docgen",
        "docs_directory": "docsDirectory",
        "entrypoint_types": "entrypointTypes",
        "eslint": "eslint",
        "eslint_options": "eslintOptions",
        "libdir": "libdir",
        "projenrc_ts": "projenrcTs",
        "projenrc_ts_options": "projenrcTsOptions",
        "sample_code": "sampleCode",
        "srcdir": "srcdir",
        "testdir": "testdir",
        "tsconfig": "tsconfig",
        "tsconfig_dev": "tsconfigDev",
        "tsconfig_dev_file": "tsconfigDevFile",
        "typescript_version": "typescriptVersion",
        "monorepo_upgrade_deps": "monorepoUpgradeDeps",
        "monorepo_upgrade_deps_options": "monorepoUpgradeDepsOptions",
        "workspace_config": "workspaceConfig",
    },
)
class NxMonorepoProjectOptions(_projen_typescript_04054675.TypeScriptProjectOptions):
    def __init__(
        self,
        *,
        name: builtins.str,
        commit_generated: typing.Optional[builtins.bool] = None,
        git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_projen_04054675.Project] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        auto_approve_options: typing.Optional[typing.Union[_projen_github_04054675.AutoApproveOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        auto_merge: typing.Optional[builtins.bool] = None,
        auto_merge_options: typing.Optional[typing.Union[_projen_github_04054675.AutoMergeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[typing.Union[_projen_github_04054675.GitHubOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[typing.Union[_projen_github_04054675.MergifyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        project_type: typing.Optional[_projen_04054675.ProjectType] = None,
        projen_credentials: typing.Optional[_projen_github_04054675.GithubCredentials] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        readme: typing.Optional[typing.Union[_projen_04054675.SampleReadmeProps, typing.Dict[builtins.str, typing.Any]]] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[typing.Union[_projen_github_04054675.StaleOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        vscode: typing.Optional[builtins.bool] = None,
        allow_library_dependencies: typing.Optional[builtins.bool] = None,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        author_organization: typing.Optional[builtins.bool] = None,
        author_url: typing.Optional[builtins.str] = None,
        auto_detect_bin: typing.Optional[builtins.bool] = None,
        bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        bugs_email: typing.Optional[builtins.str] = None,
        bugs_url: typing.Optional[builtins.str] = None,
        bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        code_artifact_options: typing.Optional[typing.Union[_projen_javascript_04054675.CodeArtifactOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        entrypoint: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        license: typing.Optional[builtins.str] = None,
        licensed: typing.Optional[builtins.bool] = None,
        max_node_version: typing.Optional[builtins.str] = None,
        min_node_version: typing.Optional[builtins.str] = None,
        npm_access: typing.Optional[_projen_javascript_04054675.NpmAccess] = None,
        npm_registry: typing.Optional[builtins.str] = None,
        npm_registry_url: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        package_manager: typing.Optional[_projen_javascript_04054675.NodePackageManager] = None,
        package_name: typing.Optional[builtins.str] = None,
        peer_dependency_options: typing.Optional[typing.Union[_projen_javascript_04054675.PeerDependencyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        pnpm_version: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
        repository_directory: typing.Optional[builtins.str] = None,
        scoped_packages_options: typing.Optional[typing.Sequence[typing.Union[_projen_javascript_04054675.ScopedPackagesOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        stability: typing.Optional[builtins.str] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        min_major_version: typing.Optional[jsii.Number] = None,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        publish_dry_run: typing.Optional[builtins.bool] = None,
        publish_tasks: typing.Optional[builtins.bool] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, typing.Union[_projen_release_04054675.BranchOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_failure_issue: typing.Optional[builtins.bool] = None,
        release_failure_issue_label: typing.Optional[builtins.str] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_tag_prefix: typing.Optional[builtins.str] = None,
        release_trigger: typing.Optional[_projen_release_04054675.ReleaseTrigger] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        default_release_branch: builtins.str,
        artifacts_directory: typing.Optional[builtins.str] = None,
        auto_approve_upgrades: typing.Optional[builtins.bool] = None,
        build_workflow: typing.Optional[builtins.bool] = None,
        build_workflow_triggers: typing.Optional[typing.Union[_projen_github_workflows_04054675.Triggers, typing.Dict[builtins.str, typing.Any]]] = None,
        bundler_options: typing.Optional[typing.Union[_projen_javascript_04054675.BundlerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        code_cov: typing.Optional[builtins.bool] = None,
        code_cov_token_secret: typing.Optional[builtins.str] = None,
        copyright_owner: typing.Optional[builtins.str] = None,
        copyright_period: typing.Optional[builtins.str] = None,
        dependabot: typing.Optional[builtins.bool] = None,
        dependabot_options: typing.Optional[typing.Union[_projen_github_04054675.DependabotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        deps_upgrade: typing.Optional[builtins.bool] = None,
        deps_upgrade_options: typing.Optional[typing.Union[_projen_javascript_04054675.UpgradeDependenciesOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        jest: typing.Optional[builtins.bool] = None,
        jest_options: typing.Optional[typing.Union[_projen_javascript_04054675.JestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        mutable_build: typing.Optional[builtins.bool] = None,
        npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        npmignore_enabled: typing.Optional[builtins.bool] = None,
        npm_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        package: typing.Optional[builtins.bool] = None,
        prettier: typing.Optional[builtins.bool] = None,
        prettier_options: typing.Optional[typing.Union[_projen_javascript_04054675.PrettierOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projen_dev_dependency: typing.Optional[builtins.bool] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_js_options: typing.Optional[typing.Union[_projen_javascript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projen_version: typing.Optional[builtins.str] = None,
        pull_request_template: typing.Optional[builtins.bool] = None,
        pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
        release: typing.Optional[builtins.bool] = None,
        release_to_npm: typing.Optional[builtins.bool] = None,
        release_workflow: typing.Optional[builtins.bool] = None,
        workflow_bootstrap_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        workflow_git_identity: typing.Optional[typing.Union[_projen_github_04054675.GitIdentity, typing.Dict[builtins.str, typing.Any]]] = None,
        workflow_node_version: typing.Optional[builtins.str] = None,
        disable_tsconfig: typing.Optional[builtins.bool] = None,
        disable_tsconfig_dev: typing.Optional[builtins.bool] = None,
        docgen: typing.Optional[builtins.bool] = None,
        docs_directory: typing.Optional[builtins.str] = None,
        entrypoint_types: typing.Optional[builtins.str] = None,
        eslint: typing.Optional[builtins.bool] = None,
        eslint_options: typing.Optional[typing.Union[_projen_javascript_04054675.EslintOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        libdir: typing.Optional[builtins.str] = None,
        projenrc_ts: typing.Optional[builtins.bool] = None,
        projenrc_ts_options: typing.Optional[typing.Union[_projen_typescript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        sample_code: typing.Optional[builtins.bool] = None,
        srcdir: typing.Optional[builtins.str] = None,
        testdir: typing.Optional[builtins.str] = None,
        tsconfig: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        tsconfig_dev: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        tsconfig_dev_file: typing.Optional[builtins.str] = None,
        typescript_version: typing.Optional[builtins.str] = None,
        monorepo_upgrade_deps: typing.Optional[builtins.bool] = None,
        monorepo_upgrade_deps_options: typing.Optional[typing.Union[MonorepoUpgradeDepsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        workspace_config: typing.Optional[typing.Union["WorkspaceConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Configuration options for the NxMonorepoProject.

        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param commit_generated: (experimental) Whether to commit the managed files by default. Default: true
        :param git_ignore_options: (experimental) Configuration options for .gitignore file.
        :param git_options: (experimental) Configuration options for git.
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge: (experimental) Enable automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: true
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` or ``autoMerge`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: - true, but false for subprojects
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_credentials: (experimental) Choose a method of providing GitHub API access for projen workflows. Default: - use a personal access token named PROJEN_GITHUB_TOKEN
        :param projen_token_secret: (deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: false
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param allow_library_dependencies: (experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``. This is normally only allowed for libraries. For apps, there's no meaning for specifying these. Default: true
        :param author_email: (experimental) Author's e-mail.
        :param author_name: (experimental) Author's name.
        :param author_organization: (experimental) Is the author an organization.
        :param author_url: (experimental) Author's URL / Website.
        :param auto_detect_bin: (experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section. Default: true
        :param bin: (experimental) Binary programs vended with your module. You can use this option to add/customize how binaries are represented in your ``package.json``, but unless ``autoDetectBin`` is ``false``, every executable file under ``bin`` will automatically be added to this section.
        :param bugs_email: (experimental) The email address to which issues should be reported.
        :param bugs_url: (experimental) The url to your project's issue tracker.
        :param bundled_deps: (experimental) List of dependencies to bundle into this module. These modules will be added both to the ``dependencies`` section and ``bundledDependencies`` section of your ``package.json``. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include.
        :param code_artifact_options: (experimental) Options for npm packages using AWS CodeArtifact. This is required if publishing packages to, or installing scoped packages from AWS CodeArtifact Default: - undefined
        :param deps: (experimental) Runtime dependencies of this module. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param description: (experimental) The description is just a string that helps people understand the purpose of the package. It can be used when searching for packages in a package manager as well. See https://classic.yarnpkg.com/en/docs/package-json/#toc-description
        :param dev_deps: (experimental) Build dependencies for this module. These dependencies will only be available in your build environment but will not be fetched when this module is consumed. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param entrypoint: (experimental) Module entrypoint (``main`` in ``package.json``). Set to an empty string to not include ``main`` in your package.json Default: "lib/index.js"
        :param homepage: (experimental) Package's Homepage / Website.
        :param keywords: (experimental) Keywords to include in ``package.json``.
        :param license: (experimental) License's SPDX identifier. See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses. Use the ``licensed`` option if you want to no license to be specified. Default: "Apache-2.0"
        :param licensed: (experimental) Indicates if a license should be added. Default: true
        :param max_node_version: (experimental) Minimum node.js version to require via ``engines`` (inclusive). Default: - no max
        :param min_node_version: (experimental) Minimum Node.js version to require via package.json ``engines`` (inclusive). Default: - no "engines" specified
        :param npm_access: (experimental) Access level of the npm package. Default: - for scoped packages (e.g. ``foo@bar``), the default is ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is ``NpmAccess.PUBLIC``.
        :param npm_registry: (deprecated) The host name of the npm registry to publish to. Cannot be set together with ``npmRegistryUrl``.
        :param npm_registry_url: (experimental) The base URL of the npm package registry. Must be a URL (e.g. start with "https://" or "http://") Default: "https://registry.npmjs.org"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: "NPM_TOKEN"
        :param package_manager: (experimental) The Node Package Manager used to execute scripts. Default: NodePackageManager.YARN
        :param package_name: (experimental) The "name" in package.json. Default: - defaults to project name
        :param peer_dependency_options: (experimental) Options for ``peerDeps``.
        :param peer_deps: (experimental) Peer dependencies for this module. Dependencies listed here are required to be installed (and satisfied) by the *consumer* of this library. Using peer dependencies allows you to ensure that only a single module of a certain library exists in the ``node_modules`` tree of your consumers. Note that prior to npm@7, peer dependencies are *not* automatically installed, which means that adding peer dependencies to a library will be a breaking change for your customers. Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is enabled by default), projen will automatically add a dev dependency with a pinned version for each peer dependency. This will ensure that you build & test your module against the lowest peer version required. Default: []
        :param pnpm_version: (experimental) The version of PNPM to use if using PNPM as a package manager. Default: "7"
        :param repository: (experimental) The repository is the location where the actual code for your package lives. See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository
        :param repository_directory: (experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.
        :param scoped_packages_options: (experimental) Options for privately hosted scoped packages. Default: - fetch all scoped packages from the public npm registry
        :param scripts: (deprecated) npm scripts to include. If a script has the same name as a standard script, the standard script will be overwritten. Also adds the script as a task. Default: {}
        :param stability: (experimental) Package's Stability.
        :param jsii_release_version: (experimental) Version requirement of ``publib`` which is used to publish modules to npm. Default: "latest"
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param min_major_version: (experimental) Minimal Major version to release. This can be useful to set to 1, as breaking changes before the 1.x major release are not incrementing the major version number. Can not be set together with ``majorVersion``. Default: - No minimum version is being enforced
        :param npm_dist_tag: (experimental) The npmDistTag to use when publishing from the default branch. To set the npm dist-tag for release branches, set the ``npmDistTag`` property for each branch. Default: "latest"
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param publish_dry_run: (experimental) Instead of actually publishing to package managers, just print the publishing command. Default: false
        :param publish_tasks: (experimental) Define publishing tasks that can be executed manually as well as workflows. Normally, publishing only happens within automated workflows. Enable this in order to create a publishing task for each publishing activity. Default: false
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_failure_issue: (experimental) Create a github issue on every failed publishing task. Default: false
        :param release_failure_issue_label: (experimental) The label to apply to issues indicating publish failures. Only applies if ``releaseFailureIssue`` is true. Default: "failed-release"
        :param release_schedule: (deprecated) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_tag_prefix: (experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers. Note: this prefix is used to detect the latest tagged version when bumping, so if you change this on a project with an existing version history, you may need to manually tag your latest release with the new prefix. Default: "v"
        :param release_trigger: (experimental) The release trigger to use. Default: - Continuous releases (``ReleaseTrigger.continuous()``)
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "Release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param versionrc_options: (experimental) Custom configuration used when creating changelog with standard-version package. Given values either append to default configuration or overwrite values in it. Default: - standard configuration applicable for GitHub repositories
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param workflow_runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param default_release_branch: (experimental) The name of the main release branch. Default: "main"
        :param artifacts_directory: (experimental) A directory which will contain build artifacts. Default: "dist"
        :param auto_approve_upgrades: (experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: - true
        :param build_workflow: (experimental) Define a GitHub workflow for building PRs. Default: - true if not a subproject
        :param build_workflow_triggers: (experimental) Build workflow triggers. Default: "{ pullRequest: {}, workflowDispatch: {} }"
        :param bundler_options: (experimental) Options for ``Bundler``.
        :param code_cov: (experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v3 A secret is required for private repos. Configured with @codeCovTokenSecret. Default: false
        :param code_cov_token_secret: (experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories. Default: - if this option is not specified, only public repositories are supported
        :param copyright_owner: (experimental) License copyright owner. Default: - defaults to the value of authorName or "" if ``authorName`` is undefined.
        :param copyright_period: (experimental) The copyright years to put in the LICENSE file. Default: - current year
        :param dependabot: (experimental) Use dependabot to handle dependency upgrades. Cannot be used in conjunction with ``depsUpgrade``. Default: false
        :param dependabot_options: (experimental) Options for dependabot. Default: - default options
        :param deps_upgrade: (experimental) Use github workflows to handle dependency upgrades. Cannot be used in conjunction with ``dependabot``. Default: true
        :param deps_upgrade_options: (experimental) Options for ``UpgradeDependencies``. Default: - default options
        :param gitignore: (experimental) Additional entries to .gitignore.
        :param jest: (experimental) Setup jest unit tests. Default: true
        :param jest_options: (experimental) Jest options. Default: - default options
        :param mutable_build: (experimental) Automatically update files modified during builds to pull-request branches. This means that any files synthesized by projen or e.g. test snapshots will always be up-to-date before a PR is merged. Implies that PR builds do not have anti-tamper checks. Default: true
        :param npmignore: (deprecated) Additional entries to .npmignore.
        :param npmignore_enabled: (experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs. Default: true
        :param npm_ignore_options: (experimental) Configuration options for .npmignore file.
        :param package: (experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``). Default: true
        :param prettier: (experimental) Setup prettier. Default: false
        :param prettier_options: (experimental) Prettier options. Default: - default options
        :param projen_dev_dependency: (experimental) Indicates of "projen" should be installed as a devDependency. Default: true
        :param projenrc_js: (experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation. Default: - true if projenrcJson is false
        :param projenrc_js_options: (experimental) Options for .projenrc.js. Default: - default options
        :param projen_version: (experimental) Version of projen to install. Default: - Defaults to the latest version.
        :param pull_request_template: (experimental) Include a GitHub pull request template. Default: true
        :param pull_request_template_contents: (experimental) The contents of the pull request template. Default: - default content
        :param release: (experimental) Add release management to this project. Default: - true (false for subprojects)
        :param release_to_npm: (experimental) Automatically release to npm when new versions are introduced. Default: false
        :param release_workflow: (deprecated) DEPRECATED: renamed to ``release``. Default: - true if not a subproject
        :param workflow_bootstrap_steps: (experimental) Workflow steps to use in order to bootstrap this repo. Default: "yarn install --frozen-lockfile && yarn projen"
        :param workflow_git_identity: (experimental) The git identity to use in workflows. Default: - GitHub Actions
        :param workflow_node_version: (experimental) The node version to use in GitHub workflows. Default: - same as ``minNodeVersion``
        :param disable_tsconfig: (experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler). Default: false
        :param disable_tsconfig_dev: (experimental) Do not generate a ``tsconfig.dev.json`` file. Default: false
        :param docgen: (experimental) Docgen by Typedoc. Default: false
        :param docs_directory: (experimental) Docs directory. Default: "docs"
        :param entrypoint_types: (experimental) The .d.ts file that includes the type declarations for this module. Default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)
        :param eslint: (experimental) Setup eslint. Default: true
        :param eslint_options: (experimental) Eslint options. Default: - opinionated default options
        :param libdir: (experimental) Typescript artifacts output directory. Default: "lib"
        :param projenrc_ts: (experimental) Use TypeScript for your projenrc file (``.projenrc.ts``). Default: false
        :param projenrc_ts_options: (experimental) Options for .projenrc.ts.
        :param sample_code: (experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there. Default: true
        :param srcdir: (experimental) Typescript sources directory. Default: "src"
        :param testdir: (experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``. If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``), then tests are going to be compiled into ``lib/`` and executed as javascript. If the test directory is outside of ``src``, then we configure jest to compile the code in-memory. Default: "test"
        :param tsconfig: (experimental) Custom TSConfig. Default: - default options
        :param tsconfig_dev: (experimental) Custom tsconfig options for the development tsconfig.json file (used for testing). Default: - use the production tsconfig options
        :param tsconfig_dev_file: (experimental) The name of the development tsconfig.json file. Default: "tsconfig.dev.json"
        :param typescript_version: (experimental) TypeScript version to use. NOTE: Typescript is not semantically versioned and should remain on the same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``). Default: "latest"
        :param monorepo_upgrade_deps: Whether to include an upgrade-deps task at the root of the monorepo which will upgrade all dependencies. Default: true
        :param monorepo_upgrade_deps_options: Monorepo Upgrade Deps options. This is only used if monorepoUpgradeDeps is true. Default: undefined
        :param workspace_config: Configuration for workspace.
        '''
        if isinstance(git_ignore_options, dict):
            git_ignore_options = _projen_04054675.IgnoreFileOptions(**git_ignore_options)
        if isinstance(git_options, dict):
            git_options = _projen_04054675.GitOptions(**git_options)
        if isinstance(logging, dict):
            logging = _projen_04054675.LoggerOptions(**logging)
        if isinstance(projenrc_json_options, dict):
            projenrc_json_options = _projen_04054675.ProjenrcJsonOptions(**projenrc_json_options)
        if isinstance(renovatebot_options, dict):
            renovatebot_options = _projen_04054675.RenovatebotOptions(**renovatebot_options)
        if isinstance(auto_approve_options, dict):
            auto_approve_options = _projen_github_04054675.AutoApproveOptions(**auto_approve_options)
        if isinstance(auto_merge_options, dict):
            auto_merge_options = _projen_github_04054675.AutoMergeOptions(**auto_merge_options)
        if isinstance(github_options, dict):
            github_options = _projen_github_04054675.GitHubOptions(**github_options)
        if isinstance(mergify_options, dict):
            mergify_options = _projen_github_04054675.MergifyOptions(**mergify_options)
        if isinstance(readme, dict):
            readme = _projen_04054675.SampleReadmeProps(**readme)
        if isinstance(stale_options, dict):
            stale_options = _projen_github_04054675.StaleOptions(**stale_options)
        if isinstance(code_artifact_options, dict):
            code_artifact_options = _projen_javascript_04054675.CodeArtifactOptions(**code_artifact_options)
        if isinstance(peer_dependency_options, dict):
            peer_dependency_options = _projen_javascript_04054675.PeerDependencyOptions(**peer_dependency_options)
        if isinstance(build_workflow_triggers, dict):
            build_workflow_triggers = _projen_github_workflows_04054675.Triggers(**build_workflow_triggers)
        if isinstance(bundler_options, dict):
            bundler_options = _projen_javascript_04054675.BundlerOptions(**bundler_options)
        if isinstance(dependabot_options, dict):
            dependabot_options = _projen_github_04054675.DependabotOptions(**dependabot_options)
        if isinstance(deps_upgrade_options, dict):
            deps_upgrade_options = _projen_javascript_04054675.UpgradeDependenciesOptions(**deps_upgrade_options)
        if isinstance(jest_options, dict):
            jest_options = _projen_javascript_04054675.JestOptions(**jest_options)
        if isinstance(npm_ignore_options, dict):
            npm_ignore_options = _projen_04054675.IgnoreFileOptions(**npm_ignore_options)
        if isinstance(prettier_options, dict):
            prettier_options = _projen_javascript_04054675.PrettierOptions(**prettier_options)
        if isinstance(projenrc_js_options, dict):
            projenrc_js_options = _projen_javascript_04054675.ProjenrcOptions(**projenrc_js_options)
        if isinstance(workflow_git_identity, dict):
            workflow_git_identity = _projen_github_04054675.GitIdentity(**workflow_git_identity)
        if isinstance(eslint_options, dict):
            eslint_options = _projen_javascript_04054675.EslintOptions(**eslint_options)
        if isinstance(projenrc_ts_options, dict):
            projenrc_ts_options = _projen_typescript_04054675.ProjenrcOptions(**projenrc_ts_options)
        if isinstance(tsconfig, dict):
            tsconfig = _projen_javascript_04054675.TypescriptConfigOptions(**tsconfig)
        if isinstance(tsconfig_dev, dict):
            tsconfig_dev = _projen_javascript_04054675.TypescriptConfigOptions(**tsconfig_dev)
        if isinstance(monorepo_upgrade_deps_options, dict):
            monorepo_upgrade_deps_options = MonorepoUpgradeDepsOptions(**monorepo_upgrade_deps_options)
        if isinstance(workspace_config, dict):
            workspace_config = WorkspaceConfig(**workspace_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b076e3e97e6fa0494e8519239ca96623326e0759561b9c979aaa70fc6a588147)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument commit_generated", value=commit_generated, expected_type=type_hints["commit_generated"])
            check_type(argname="argument git_ignore_options", value=git_ignore_options, expected_type=type_hints["git_ignore_options"])
            check_type(argname="argument git_options", value=git_options, expected_type=type_hints["git_options"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
            check_type(argname="argument outdir", value=outdir, expected_type=type_hints["outdir"])
            check_type(argname="argument parent", value=parent, expected_type=type_hints["parent"])
            check_type(argname="argument projen_command", value=projen_command, expected_type=type_hints["projen_command"])
            check_type(argname="argument projenrc_json", value=projenrc_json, expected_type=type_hints["projenrc_json"])
            check_type(argname="argument projenrc_json_options", value=projenrc_json_options, expected_type=type_hints["projenrc_json_options"])
            check_type(argname="argument renovatebot", value=renovatebot, expected_type=type_hints["renovatebot"])
            check_type(argname="argument renovatebot_options", value=renovatebot_options, expected_type=type_hints["renovatebot_options"])
            check_type(argname="argument auto_approve_options", value=auto_approve_options, expected_type=type_hints["auto_approve_options"])
            check_type(argname="argument auto_merge", value=auto_merge, expected_type=type_hints["auto_merge"])
            check_type(argname="argument auto_merge_options", value=auto_merge_options, expected_type=type_hints["auto_merge_options"])
            check_type(argname="argument clobber", value=clobber, expected_type=type_hints["clobber"])
            check_type(argname="argument dev_container", value=dev_container, expected_type=type_hints["dev_container"])
            check_type(argname="argument github", value=github, expected_type=type_hints["github"])
            check_type(argname="argument github_options", value=github_options, expected_type=type_hints["github_options"])
            check_type(argname="argument gitpod", value=gitpod, expected_type=type_hints["gitpod"])
            check_type(argname="argument mergify", value=mergify, expected_type=type_hints["mergify"])
            check_type(argname="argument mergify_options", value=mergify_options, expected_type=type_hints["mergify_options"])
            check_type(argname="argument project_type", value=project_type, expected_type=type_hints["project_type"])
            check_type(argname="argument projen_credentials", value=projen_credentials, expected_type=type_hints["projen_credentials"])
            check_type(argname="argument projen_token_secret", value=projen_token_secret, expected_type=type_hints["projen_token_secret"])
            check_type(argname="argument readme", value=readme, expected_type=type_hints["readme"])
            check_type(argname="argument stale", value=stale, expected_type=type_hints["stale"])
            check_type(argname="argument stale_options", value=stale_options, expected_type=type_hints["stale_options"])
            check_type(argname="argument vscode", value=vscode, expected_type=type_hints["vscode"])
            check_type(argname="argument allow_library_dependencies", value=allow_library_dependencies, expected_type=type_hints["allow_library_dependencies"])
            check_type(argname="argument author_email", value=author_email, expected_type=type_hints["author_email"])
            check_type(argname="argument author_name", value=author_name, expected_type=type_hints["author_name"])
            check_type(argname="argument author_organization", value=author_organization, expected_type=type_hints["author_organization"])
            check_type(argname="argument author_url", value=author_url, expected_type=type_hints["author_url"])
            check_type(argname="argument auto_detect_bin", value=auto_detect_bin, expected_type=type_hints["auto_detect_bin"])
            check_type(argname="argument bin", value=bin, expected_type=type_hints["bin"])
            check_type(argname="argument bugs_email", value=bugs_email, expected_type=type_hints["bugs_email"])
            check_type(argname="argument bugs_url", value=bugs_url, expected_type=type_hints["bugs_url"])
            check_type(argname="argument bundled_deps", value=bundled_deps, expected_type=type_hints["bundled_deps"])
            check_type(argname="argument code_artifact_options", value=code_artifact_options, expected_type=type_hints["code_artifact_options"])
            check_type(argname="argument deps", value=deps, expected_type=type_hints["deps"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument dev_deps", value=dev_deps, expected_type=type_hints["dev_deps"])
            check_type(argname="argument entrypoint", value=entrypoint, expected_type=type_hints["entrypoint"])
            check_type(argname="argument homepage", value=homepage, expected_type=type_hints["homepage"])
            check_type(argname="argument keywords", value=keywords, expected_type=type_hints["keywords"])
            check_type(argname="argument license", value=license, expected_type=type_hints["license"])
            check_type(argname="argument licensed", value=licensed, expected_type=type_hints["licensed"])
            check_type(argname="argument max_node_version", value=max_node_version, expected_type=type_hints["max_node_version"])
            check_type(argname="argument min_node_version", value=min_node_version, expected_type=type_hints["min_node_version"])
            check_type(argname="argument npm_access", value=npm_access, expected_type=type_hints["npm_access"])
            check_type(argname="argument npm_registry", value=npm_registry, expected_type=type_hints["npm_registry"])
            check_type(argname="argument npm_registry_url", value=npm_registry_url, expected_type=type_hints["npm_registry_url"])
            check_type(argname="argument npm_token_secret", value=npm_token_secret, expected_type=type_hints["npm_token_secret"])
            check_type(argname="argument package_manager", value=package_manager, expected_type=type_hints["package_manager"])
            check_type(argname="argument package_name", value=package_name, expected_type=type_hints["package_name"])
            check_type(argname="argument peer_dependency_options", value=peer_dependency_options, expected_type=type_hints["peer_dependency_options"])
            check_type(argname="argument peer_deps", value=peer_deps, expected_type=type_hints["peer_deps"])
            check_type(argname="argument pnpm_version", value=pnpm_version, expected_type=type_hints["pnpm_version"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument repository_directory", value=repository_directory, expected_type=type_hints["repository_directory"])
            check_type(argname="argument scoped_packages_options", value=scoped_packages_options, expected_type=type_hints["scoped_packages_options"])
            check_type(argname="argument scripts", value=scripts, expected_type=type_hints["scripts"])
            check_type(argname="argument stability", value=stability, expected_type=type_hints["stability"])
            check_type(argname="argument jsii_release_version", value=jsii_release_version, expected_type=type_hints["jsii_release_version"])
            check_type(argname="argument major_version", value=major_version, expected_type=type_hints["major_version"])
            check_type(argname="argument min_major_version", value=min_major_version, expected_type=type_hints["min_major_version"])
            check_type(argname="argument npm_dist_tag", value=npm_dist_tag, expected_type=type_hints["npm_dist_tag"])
            check_type(argname="argument post_build_steps", value=post_build_steps, expected_type=type_hints["post_build_steps"])
            check_type(argname="argument prerelease", value=prerelease, expected_type=type_hints["prerelease"])
            check_type(argname="argument publish_dry_run", value=publish_dry_run, expected_type=type_hints["publish_dry_run"])
            check_type(argname="argument publish_tasks", value=publish_tasks, expected_type=type_hints["publish_tasks"])
            check_type(argname="argument release_branches", value=release_branches, expected_type=type_hints["release_branches"])
            check_type(argname="argument release_every_commit", value=release_every_commit, expected_type=type_hints["release_every_commit"])
            check_type(argname="argument release_failure_issue", value=release_failure_issue, expected_type=type_hints["release_failure_issue"])
            check_type(argname="argument release_failure_issue_label", value=release_failure_issue_label, expected_type=type_hints["release_failure_issue_label"])
            check_type(argname="argument release_schedule", value=release_schedule, expected_type=type_hints["release_schedule"])
            check_type(argname="argument release_tag_prefix", value=release_tag_prefix, expected_type=type_hints["release_tag_prefix"])
            check_type(argname="argument release_trigger", value=release_trigger, expected_type=type_hints["release_trigger"])
            check_type(argname="argument release_workflow_name", value=release_workflow_name, expected_type=type_hints["release_workflow_name"])
            check_type(argname="argument release_workflow_setup_steps", value=release_workflow_setup_steps, expected_type=type_hints["release_workflow_setup_steps"])
            check_type(argname="argument versionrc_options", value=versionrc_options, expected_type=type_hints["versionrc_options"])
            check_type(argname="argument workflow_container_image", value=workflow_container_image, expected_type=type_hints["workflow_container_image"])
            check_type(argname="argument workflow_runs_on", value=workflow_runs_on, expected_type=type_hints["workflow_runs_on"])
            check_type(argname="argument default_release_branch", value=default_release_branch, expected_type=type_hints["default_release_branch"])
            check_type(argname="argument artifacts_directory", value=artifacts_directory, expected_type=type_hints["artifacts_directory"])
            check_type(argname="argument auto_approve_upgrades", value=auto_approve_upgrades, expected_type=type_hints["auto_approve_upgrades"])
            check_type(argname="argument build_workflow", value=build_workflow, expected_type=type_hints["build_workflow"])
            check_type(argname="argument build_workflow_triggers", value=build_workflow_triggers, expected_type=type_hints["build_workflow_triggers"])
            check_type(argname="argument bundler_options", value=bundler_options, expected_type=type_hints["bundler_options"])
            check_type(argname="argument code_cov", value=code_cov, expected_type=type_hints["code_cov"])
            check_type(argname="argument code_cov_token_secret", value=code_cov_token_secret, expected_type=type_hints["code_cov_token_secret"])
            check_type(argname="argument copyright_owner", value=copyright_owner, expected_type=type_hints["copyright_owner"])
            check_type(argname="argument copyright_period", value=copyright_period, expected_type=type_hints["copyright_period"])
            check_type(argname="argument dependabot", value=dependabot, expected_type=type_hints["dependabot"])
            check_type(argname="argument dependabot_options", value=dependabot_options, expected_type=type_hints["dependabot_options"])
            check_type(argname="argument deps_upgrade", value=deps_upgrade, expected_type=type_hints["deps_upgrade"])
            check_type(argname="argument deps_upgrade_options", value=deps_upgrade_options, expected_type=type_hints["deps_upgrade_options"])
            check_type(argname="argument gitignore", value=gitignore, expected_type=type_hints["gitignore"])
            check_type(argname="argument jest", value=jest, expected_type=type_hints["jest"])
            check_type(argname="argument jest_options", value=jest_options, expected_type=type_hints["jest_options"])
            check_type(argname="argument mutable_build", value=mutable_build, expected_type=type_hints["mutable_build"])
            check_type(argname="argument npmignore", value=npmignore, expected_type=type_hints["npmignore"])
            check_type(argname="argument npmignore_enabled", value=npmignore_enabled, expected_type=type_hints["npmignore_enabled"])
            check_type(argname="argument npm_ignore_options", value=npm_ignore_options, expected_type=type_hints["npm_ignore_options"])
            check_type(argname="argument package", value=package, expected_type=type_hints["package"])
            check_type(argname="argument prettier", value=prettier, expected_type=type_hints["prettier"])
            check_type(argname="argument prettier_options", value=prettier_options, expected_type=type_hints["prettier_options"])
            check_type(argname="argument projen_dev_dependency", value=projen_dev_dependency, expected_type=type_hints["projen_dev_dependency"])
            check_type(argname="argument projenrc_js", value=projenrc_js, expected_type=type_hints["projenrc_js"])
            check_type(argname="argument projenrc_js_options", value=projenrc_js_options, expected_type=type_hints["projenrc_js_options"])
            check_type(argname="argument projen_version", value=projen_version, expected_type=type_hints["projen_version"])
            check_type(argname="argument pull_request_template", value=pull_request_template, expected_type=type_hints["pull_request_template"])
            check_type(argname="argument pull_request_template_contents", value=pull_request_template_contents, expected_type=type_hints["pull_request_template_contents"])
            check_type(argname="argument release", value=release, expected_type=type_hints["release"])
            check_type(argname="argument release_to_npm", value=release_to_npm, expected_type=type_hints["release_to_npm"])
            check_type(argname="argument release_workflow", value=release_workflow, expected_type=type_hints["release_workflow"])
            check_type(argname="argument workflow_bootstrap_steps", value=workflow_bootstrap_steps, expected_type=type_hints["workflow_bootstrap_steps"])
            check_type(argname="argument workflow_git_identity", value=workflow_git_identity, expected_type=type_hints["workflow_git_identity"])
            check_type(argname="argument workflow_node_version", value=workflow_node_version, expected_type=type_hints["workflow_node_version"])
            check_type(argname="argument disable_tsconfig", value=disable_tsconfig, expected_type=type_hints["disable_tsconfig"])
            check_type(argname="argument disable_tsconfig_dev", value=disable_tsconfig_dev, expected_type=type_hints["disable_tsconfig_dev"])
            check_type(argname="argument docgen", value=docgen, expected_type=type_hints["docgen"])
            check_type(argname="argument docs_directory", value=docs_directory, expected_type=type_hints["docs_directory"])
            check_type(argname="argument entrypoint_types", value=entrypoint_types, expected_type=type_hints["entrypoint_types"])
            check_type(argname="argument eslint", value=eslint, expected_type=type_hints["eslint"])
            check_type(argname="argument eslint_options", value=eslint_options, expected_type=type_hints["eslint_options"])
            check_type(argname="argument libdir", value=libdir, expected_type=type_hints["libdir"])
            check_type(argname="argument projenrc_ts", value=projenrc_ts, expected_type=type_hints["projenrc_ts"])
            check_type(argname="argument projenrc_ts_options", value=projenrc_ts_options, expected_type=type_hints["projenrc_ts_options"])
            check_type(argname="argument sample_code", value=sample_code, expected_type=type_hints["sample_code"])
            check_type(argname="argument srcdir", value=srcdir, expected_type=type_hints["srcdir"])
            check_type(argname="argument testdir", value=testdir, expected_type=type_hints["testdir"])
            check_type(argname="argument tsconfig", value=tsconfig, expected_type=type_hints["tsconfig"])
            check_type(argname="argument tsconfig_dev", value=tsconfig_dev, expected_type=type_hints["tsconfig_dev"])
            check_type(argname="argument tsconfig_dev_file", value=tsconfig_dev_file, expected_type=type_hints["tsconfig_dev_file"])
            check_type(argname="argument typescript_version", value=typescript_version, expected_type=type_hints["typescript_version"])
            check_type(argname="argument monorepo_upgrade_deps", value=monorepo_upgrade_deps, expected_type=type_hints["monorepo_upgrade_deps"])
            check_type(argname="argument monorepo_upgrade_deps_options", value=monorepo_upgrade_deps_options, expected_type=type_hints["monorepo_upgrade_deps_options"])
            check_type(argname="argument workspace_config", value=workspace_config, expected_type=type_hints["workspace_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "default_release_branch": default_release_branch,
        }
        if commit_generated is not None:
            self._values["commit_generated"] = commit_generated
        if git_ignore_options is not None:
            self._values["git_ignore_options"] = git_ignore_options
        if git_options is not None:
            self._values["git_options"] = git_options
        if logging is not None:
            self._values["logging"] = logging
        if outdir is not None:
            self._values["outdir"] = outdir
        if parent is not None:
            self._values["parent"] = parent
        if projen_command is not None:
            self._values["projen_command"] = projen_command
        if projenrc_json is not None:
            self._values["projenrc_json"] = projenrc_json
        if projenrc_json_options is not None:
            self._values["projenrc_json_options"] = projenrc_json_options
        if renovatebot is not None:
            self._values["renovatebot"] = renovatebot
        if renovatebot_options is not None:
            self._values["renovatebot_options"] = renovatebot_options
        if auto_approve_options is not None:
            self._values["auto_approve_options"] = auto_approve_options
        if auto_merge is not None:
            self._values["auto_merge"] = auto_merge
        if auto_merge_options is not None:
            self._values["auto_merge_options"] = auto_merge_options
        if clobber is not None:
            self._values["clobber"] = clobber
        if dev_container is not None:
            self._values["dev_container"] = dev_container
        if github is not None:
            self._values["github"] = github
        if github_options is not None:
            self._values["github_options"] = github_options
        if gitpod is not None:
            self._values["gitpod"] = gitpod
        if mergify is not None:
            self._values["mergify"] = mergify
        if mergify_options is not None:
            self._values["mergify_options"] = mergify_options
        if project_type is not None:
            self._values["project_type"] = project_type
        if projen_credentials is not None:
            self._values["projen_credentials"] = projen_credentials
        if projen_token_secret is not None:
            self._values["projen_token_secret"] = projen_token_secret
        if readme is not None:
            self._values["readme"] = readme
        if stale is not None:
            self._values["stale"] = stale
        if stale_options is not None:
            self._values["stale_options"] = stale_options
        if vscode is not None:
            self._values["vscode"] = vscode
        if allow_library_dependencies is not None:
            self._values["allow_library_dependencies"] = allow_library_dependencies
        if author_email is not None:
            self._values["author_email"] = author_email
        if author_name is not None:
            self._values["author_name"] = author_name
        if author_organization is not None:
            self._values["author_organization"] = author_organization
        if author_url is not None:
            self._values["author_url"] = author_url
        if auto_detect_bin is not None:
            self._values["auto_detect_bin"] = auto_detect_bin
        if bin is not None:
            self._values["bin"] = bin
        if bugs_email is not None:
            self._values["bugs_email"] = bugs_email
        if bugs_url is not None:
            self._values["bugs_url"] = bugs_url
        if bundled_deps is not None:
            self._values["bundled_deps"] = bundled_deps
        if code_artifact_options is not None:
            self._values["code_artifact_options"] = code_artifact_options
        if deps is not None:
            self._values["deps"] = deps
        if description is not None:
            self._values["description"] = description
        if dev_deps is not None:
            self._values["dev_deps"] = dev_deps
        if entrypoint is not None:
            self._values["entrypoint"] = entrypoint
        if homepage is not None:
            self._values["homepage"] = homepage
        if keywords is not None:
            self._values["keywords"] = keywords
        if license is not None:
            self._values["license"] = license
        if licensed is not None:
            self._values["licensed"] = licensed
        if max_node_version is not None:
            self._values["max_node_version"] = max_node_version
        if min_node_version is not None:
            self._values["min_node_version"] = min_node_version
        if npm_access is not None:
            self._values["npm_access"] = npm_access
        if npm_registry is not None:
            self._values["npm_registry"] = npm_registry
        if npm_registry_url is not None:
            self._values["npm_registry_url"] = npm_registry_url
        if npm_token_secret is not None:
            self._values["npm_token_secret"] = npm_token_secret
        if package_manager is not None:
            self._values["package_manager"] = package_manager
        if package_name is not None:
            self._values["package_name"] = package_name
        if peer_dependency_options is not None:
            self._values["peer_dependency_options"] = peer_dependency_options
        if peer_deps is not None:
            self._values["peer_deps"] = peer_deps
        if pnpm_version is not None:
            self._values["pnpm_version"] = pnpm_version
        if repository is not None:
            self._values["repository"] = repository
        if repository_directory is not None:
            self._values["repository_directory"] = repository_directory
        if scoped_packages_options is not None:
            self._values["scoped_packages_options"] = scoped_packages_options
        if scripts is not None:
            self._values["scripts"] = scripts
        if stability is not None:
            self._values["stability"] = stability
        if jsii_release_version is not None:
            self._values["jsii_release_version"] = jsii_release_version
        if major_version is not None:
            self._values["major_version"] = major_version
        if min_major_version is not None:
            self._values["min_major_version"] = min_major_version
        if npm_dist_tag is not None:
            self._values["npm_dist_tag"] = npm_dist_tag
        if post_build_steps is not None:
            self._values["post_build_steps"] = post_build_steps
        if prerelease is not None:
            self._values["prerelease"] = prerelease
        if publish_dry_run is not None:
            self._values["publish_dry_run"] = publish_dry_run
        if publish_tasks is not None:
            self._values["publish_tasks"] = publish_tasks
        if release_branches is not None:
            self._values["release_branches"] = release_branches
        if release_every_commit is not None:
            self._values["release_every_commit"] = release_every_commit
        if release_failure_issue is not None:
            self._values["release_failure_issue"] = release_failure_issue
        if release_failure_issue_label is not None:
            self._values["release_failure_issue_label"] = release_failure_issue_label
        if release_schedule is not None:
            self._values["release_schedule"] = release_schedule
        if release_tag_prefix is not None:
            self._values["release_tag_prefix"] = release_tag_prefix
        if release_trigger is not None:
            self._values["release_trigger"] = release_trigger
        if release_workflow_name is not None:
            self._values["release_workflow_name"] = release_workflow_name
        if release_workflow_setup_steps is not None:
            self._values["release_workflow_setup_steps"] = release_workflow_setup_steps
        if versionrc_options is not None:
            self._values["versionrc_options"] = versionrc_options
        if workflow_container_image is not None:
            self._values["workflow_container_image"] = workflow_container_image
        if workflow_runs_on is not None:
            self._values["workflow_runs_on"] = workflow_runs_on
        if artifacts_directory is not None:
            self._values["artifacts_directory"] = artifacts_directory
        if auto_approve_upgrades is not None:
            self._values["auto_approve_upgrades"] = auto_approve_upgrades
        if build_workflow is not None:
            self._values["build_workflow"] = build_workflow
        if build_workflow_triggers is not None:
            self._values["build_workflow_triggers"] = build_workflow_triggers
        if bundler_options is not None:
            self._values["bundler_options"] = bundler_options
        if code_cov is not None:
            self._values["code_cov"] = code_cov
        if code_cov_token_secret is not None:
            self._values["code_cov_token_secret"] = code_cov_token_secret
        if copyright_owner is not None:
            self._values["copyright_owner"] = copyright_owner
        if copyright_period is not None:
            self._values["copyright_period"] = copyright_period
        if dependabot is not None:
            self._values["dependabot"] = dependabot
        if dependabot_options is not None:
            self._values["dependabot_options"] = dependabot_options
        if deps_upgrade is not None:
            self._values["deps_upgrade"] = deps_upgrade
        if deps_upgrade_options is not None:
            self._values["deps_upgrade_options"] = deps_upgrade_options
        if gitignore is not None:
            self._values["gitignore"] = gitignore
        if jest is not None:
            self._values["jest"] = jest
        if jest_options is not None:
            self._values["jest_options"] = jest_options
        if mutable_build is not None:
            self._values["mutable_build"] = mutable_build
        if npmignore is not None:
            self._values["npmignore"] = npmignore
        if npmignore_enabled is not None:
            self._values["npmignore_enabled"] = npmignore_enabled
        if npm_ignore_options is not None:
            self._values["npm_ignore_options"] = npm_ignore_options
        if package is not None:
            self._values["package"] = package
        if prettier is not None:
            self._values["prettier"] = prettier
        if prettier_options is not None:
            self._values["prettier_options"] = prettier_options
        if projen_dev_dependency is not None:
            self._values["projen_dev_dependency"] = projen_dev_dependency
        if projenrc_js is not None:
            self._values["projenrc_js"] = projenrc_js
        if projenrc_js_options is not None:
            self._values["projenrc_js_options"] = projenrc_js_options
        if projen_version is not None:
            self._values["projen_version"] = projen_version
        if pull_request_template is not None:
            self._values["pull_request_template"] = pull_request_template
        if pull_request_template_contents is not None:
            self._values["pull_request_template_contents"] = pull_request_template_contents
        if release is not None:
            self._values["release"] = release
        if release_to_npm is not None:
            self._values["release_to_npm"] = release_to_npm
        if release_workflow is not None:
            self._values["release_workflow"] = release_workflow
        if workflow_bootstrap_steps is not None:
            self._values["workflow_bootstrap_steps"] = workflow_bootstrap_steps
        if workflow_git_identity is not None:
            self._values["workflow_git_identity"] = workflow_git_identity
        if workflow_node_version is not None:
            self._values["workflow_node_version"] = workflow_node_version
        if disable_tsconfig is not None:
            self._values["disable_tsconfig"] = disable_tsconfig
        if disable_tsconfig_dev is not None:
            self._values["disable_tsconfig_dev"] = disable_tsconfig_dev
        if docgen is not None:
            self._values["docgen"] = docgen
        if docs_directory is not None:
            self._values["docs_directory"] = docs_directory
        if entrypoint_types is not None:
            self._values["entrypoint_types"] = entrypoint_types
        if eslint is not None:
            self._values["eslint"] = eslint
        if eslint_options is not None:
            self._values["eslint_options"] = eslint_options
        if libdir is not None:
            self._values["libdir"] = libdir
        if projenrc_ts is not None:
            self._values["projenrc_ts"] = projenrc_ts
        if projenrc_ts_options is not None:
            self._values["projenrc_ts_options"] = projenrc_ts_options
        if sample_code is not None:
            self._values["sample_code"] = sample_code
        if srcdir is not None:
            self._values["srcdir"] = srcdir
        if testdir is not None:
            self._values["testdir"] = testdir
        if tsconfig is not None:
            self._values["tsconfig"] = tsconfig
        if tsconfig_dev is not None:
            self._values["tsconfig_dev"] = tsconfig_dev
        if tsconfig_dev_file is not None:
            self._values["tsconfig_dev_file"] = tsconfig_dev_file
        if typescript_version is not None:
            self._values["typescript_version"] = typescript_version
        if monorepo_upgrade_deps is not None:
            self._values["monorepo_upgrade_deps"] = monorepo_upgrade_deps
        if monorepo_upgrade_deps_options is not None:
            self._values["monorepo_upgrade_deps_options"] = monorepo_upgrade_deps_options
        if workspace_config is not None:
            self._values["workspace_config"] = workspace_config

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) This is the name of your project.

        :default: $BASEDIR

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def commit_generated(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to commit the managed files by default.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("commit_generated")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def git_ignore_options(self) -> typing.Optional[_projen_04054675.IgnoreFileOptions]:
        '''(experimental) Configuration options for .gitignore file.

        :stability: experimental
        '''
        result = self._values.get("git_ignore_options")
        return typing.cast(typing.Optional[_projen_04054675.IgnoreFileOptions], result)

    @builtins.property
    def git_options(self) -> typing.Optional[_projen_04054675.GitOptions]:
        '''(experimental) Configuration options for git.

        :stability: experimental
        '''
        result = self._values.get("git_options")
        return typing.cast(typing.Optional[_projen_04054675.GitOptions], result)

    @builtins.property
    def logging(self) -> typing.Optional[_projen_04054675.LoggerOptions]:
        '''(experimental) Configure logging options such as verbosity.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[_projen_04054675.LoggerOptions], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The root directory of the project.

        Relative to this directory, all files are synthesized.

        If this project has a parent, this directory is relative to the parent
        directory and it cannot be the same as the parent or any of it's other
        sub-projects.

        :default: "."

        :stability: experimental
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[_projen_04054675.Project]:
        '''(experimental) The parent project, if this project is part of a bigger project.

        :stability: experimental
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[_projen_04054675.Project], result)

    @builtins.property
    def projen_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) The shell command to use in order to run the projen CLI.

        Can be used to customize in special environments.

        :default: "npx projen"

        :stability: experimental
        '''
        result = self._values.get("projen_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projenrc_json(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json_options(
        self,
    ) -> typing.Optional[_projen_04054675.ProjenrcJsonOptions]:
        '''(experimental) Options for .projenrc.json.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_json_options")
        return typing.cast(typing.Optional[_projen_04054675.ProjenrcJsonOptions], result)

    @builtins.property
    def renovatebot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use renovatebot to handle dependency upgrades.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("renovatebot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def renovatebot_options(
        self,
    ) -> typing.Optional[_projen_04054675.RenovatebotOptions]:
        '''(experimental) Options for renovatebot.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("renovatebot_options")
        return typing.cast(typing.Optional[_projen_04054675.RenovatebotOptions], result)

    @builtins.property
    def auto_approve_options(
        self,
    ) -> typing.Optional[_projen_github_04054675.AutoApproveOptions]:
        '''(experimental) Enable and configure the 'auto approve' workflow.

        :default: - auto approve is disabled

        :stability: experimental
        '''
        result = self._values.get("auto_approve_options")
        return typing.cast(typing.Optional[_projen_github_04054675.AutoApproveOptions], result)

    @builtins.property
    def auto_merge(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable automatic merging on GitHub.

        Has no effect if ``github.mergify``
        is set to false.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_merge")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_merge_options(
        self,
    ) -> typing.Optional[_projen_github_04054675.AutoMergeOptions]:
        '''(experimental) Configure options for automatic merging on GitHub.

        Has no effect if
        ``github.mergify`` or ``autoMerge`` is set to false.

        :default: - see defaults in ``AutoMergeOptions``

        :stability: experimental
        '''
        result = self._values.get("auto_merge_options")
        return typing.cast(typing.Optional[_projen_github_04054675.AutoMergeOptions], result)

    @builtins.property
    def clobber(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a ``clobber`` task which resets the repo to origin.

        :default: - true, but false for subprojects

        :stability: experimental
        '''
        result = self._values.get("clobber")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dev_container(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a VSCode development environment (used for GitHub Codespaces).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dev_container")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable GitHub integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("github")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github_options(self) -> typing.Optional[_projen_github_04054675.GitHubOptions]:
        '''(experimental) Options for GitHub integration.

        :default: - see GitHubOptions

        :stability: experimental
        '''
        result = self._values.get("github_options")
        return typing.cast(typing.Optional[_projen_github_04054675.GitHubOptions], result)

    @builtins.property
    def gitpod(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a Gitpod development environment.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("gitpod")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether mergify should be enabled on this repository or not.

        :default: true

        :deprecated: use ``githubOptions.mergify`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify_options(
        self,
    ) -> typing.Optional[_projen_github_04054675.MergifyOptions]:
        '''(deprecated) Options for mergify.

        :default: - default options

        :deprecated: use ``githubOptions.mergifyOptions`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify_options")
        return typing.cast(typing.Optional[_projen_github_04054675.MergifyOptions], result)

    @builtins.property
    def project_type(self) -> typing.Optional[_projen_04054675.ProjectType]:
        '''(deprecated) Which type of project this is (library/app).

        :default: ProjectType.UNKNOWN

        :deprecated: no longer supported at the base project level

        :stability: deprecated
        '''
        result = self._values.get("project_type")
        return typing.cast(typing.Optional[_projen_04054675.ProjectType], result)

    @builtins.property
    def projen_credentials(
        self,
    ) -> typing.Optional[_projen_github_04054675.GithubCredentials]:
        '''(experimental) Choose a method of providing GitHub API access for projen workflows.

        :default: - use a personal access token named PROJEN_GITHUB_TOKEN

        :stability: experimental
        '''
        result = self._values.get("projen_credentials")
        return typing.cast(typing.Optional[_projen_github_04054675.GithubCredentials], result)

    @builtins.property
    def projen_token_secret(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows.

        This token needs to have the ``repo``, ``workflows``
        and ``packages`` scope.

        :default: "PROJEN_GITHUB_TOKEN"

        :deprecated: use ``projenCredentials``

        :stability: deprecated
        '''
        result = self._values.get("projen_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def readme(self) -> typing.Optional[_projen_04054675.SampleReadmeProps]:
        '''(experimental) The README setup.

        :default: - { filename: 'README.md', contents: '# replace this' }

        :stability: experimental

        Example::

            "{ filename: 'readme.md', contents: '# title' }"
        '''
        result = self._values.get("readme")
        return typing.cast(typing.Optional[_projen_04054675.SampleReadmeProps], result)

    @builtins.property
    def stale(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Auto-close of stale issues and pull request.

        See ``staleOptions`` for options.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("stale")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stale_options(self) -> typing.Optional[_projen_github_04054675.StaleOptions]:
        '''(experimental) Auto-close stale issues and pull requests.

        To disable set ``stale`` to ``false``.

        :default: - see defaults in ``StaleOptions``

        :stability: experimental
        '''
        result = self._values.get("stale_options")
        return typing.cast(typing.Optional[_projen_github_04054675.StaleOptions], result)

    @builtins.property
    def vscode(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable VSCode integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("vscode")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_library_dependencies(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``.

        This is normally only allowed for libraries. For apps, there's no meaning
        for specifying these.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("allow_library_dependencies")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def author_email(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's e-mail.

        :stability: experimental
        '''
        result = self._values.get("author_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's name.

        :stability: experimental
        '''
        result = self._values.get("author_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_organization(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Is the author an organization.

        :stability: experimental
        '''
        result = self._values.get("author_organization")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def author_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's URL / Website.

        :stability: experimental
        '''
        result = self._values.get("author_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_detect_bin(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_detect_bin")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def bin(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Binary programs vended with your module.

        You can use this option to add/customize how binaries are represented in
        your ``package.json``, but unless ``autoDetectBin`` is ``false``, every
        executable file under ``bin`` will automatically be added to this section.

        :stability: experimental
        '''
        result = self._values.get("bin")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def bugs_email(self) -> typing.Optional[builtins.str]:
        '''(experimental) The email address to which issues should be reported.

        :stability: experimental
        '''
        result = self._values.get("bugs_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bugs_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The url to your project's issue tracker.

        :stability: experimental
        '''
        result = self._values.get("bugs_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bundled_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of dependencies to bundle into this module.

        These modules will be
        added both to the ``dependencies`` section and ``bundledDependencies`` section of
        your ``package.json``.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :stability: experimental
        '''
        result = self._values.get("bundled_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def code_artifact_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.CodeArtifactOptions]:
        '''(experimental) Options for npm packages using AWS CodeArtifact.

        This is required if publishing packages to, or installing scoped packages from AWS CodeArtifact

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("code_artifact_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.CodeArtifactOptions], result)

    @builtins.property
    def deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Runtime dependencies of this module.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :default: []

        :stability: experimental
        :featured: true

        Example::

            [ 'express', 'lodash', 'foo@^2' ]
        '''
        result = self._values.get("deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description is just a string that helps people understand the purpose of the package.

        It can be used when searching for packages in a package manager as well.
        See https://classic.yarnpkg.com/en/docs/package-json/#toc-description

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dev_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Build dependencies for this module.

        These dependencies will only be
        available in your build environment but will not be fetched when this
        module is consumed.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :default: []

        :stability: experimental
        :featured: true

        Example::

            [ 'typescript', '@types/express' ]
        '''
        result = self._values.get("dev_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def entrypoint(self) -> typing.Optional[builtins.str]:
        '''(experimental) Module entrypoint (``main`` in ``package.json``).

        Set to an empty string to not include ``main`` in your package.json

        :default: "lib/index.js"

        :stability: experimental
        '''
        result = self._values.get("entrypoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def homepage(self) -> typing.Optional[builtins.str]:
        '''(experimental) Package's Homepage / Website.

        :stability: experimental
        '''
        result = self._values.get("homepage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def keywords(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Keywords to include in ``package.json``.

        :stability: experimental
        '''
        result = self._values.get("keywords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''(experimental) License's SPDX identifier.

        See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses.
        Use the ``licensed`` option if you want to no license to be specified.

        :default: "Apache-2.0"

        :stability: experimental
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def licensed(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates if a license should be added.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("licensed")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def max_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Minimum node.js version to require via ``engines`` (inclusive).

        :default: - no max

        :stability: experimental
        '''
        result = self._values.get("max_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Minimum Node.js version to require via package.json ``engines`` (inclusive).

        :default: - no "engines" specified

        :stability: experimental
        '''
        result = self._values.get("min_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_access(self) -> typing.Optional[_projen_javascript_04054675.NpmAccess]:
        '''(experimental) Access level of the npm package.

        :default:

        - for scoped packages (e.g. ``foo@bar``), the default is
        ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is
        ``NpmAccess.PUBLIC``.

        :stability: experimental
        '''
        result = self._values.get("npm_access")
        return typing.cast(typing.Optional[_projen_javascript_04054675.NpmAccess], result)

    @builtins.property
    def npm_registry(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The host name of the npm registry to publish to.

        Cannot be set together with ``npmRegistryUrl``.

        :deprecated: use ``npmRegistryUrl`` instead

        :stability: deprecated
        '''
        result = self._values.get("npm_registry")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_registry_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The base URL of the npm package registry.

        Must be a URL (e.g. start with "https://" or "http://")

        :default: "https://registry.npmjs.org"

        :stability: experimental
        '''
        result = self._values.get("npm_registry_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret which contains the NPM token to use when publishing packages.

        :default: "NPM_TOKEN"

        :stability: experimental
        '''
        result = self._values.get("npm_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def package_manager(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.NodePackageManager]:
        '''(experimental) The Node Package Manager used to execute scripts.

        :default: NodePackageManager.YARN

        :stability: experimental
        '''
        result = self._values.get("package_manager")
        return typing.cast(typing.Optional[_projen_javascript_04054675.NodePackageManager], result)

    @builtins.property
    def package_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The "name" in package.json.

        :default: - defaults to project name

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("package_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def peer_dependency_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.PeerDependencyOptions]:
        '''(experimental) Options for ``peerDeps``.

        :stability: experimental
        '''
        result = self._values.get("peer_dependency_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.PeerDependencyOptions], result)

    @builtins.property
    def peer_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Peer dependencies for this module.

        Dependencies listed here are required to
        be installed (and satisfied) by the *consumer* of this library. Using peer
        dependencies allows you to ensure that only a single module of a certain
        library exists in the ``node_modules`` tree of your consumers.

        Note that prior to npm@7, peer dependencies are *not* automatically
        installed, which means that adding peer dependencies to a library will be a
        breaking change for your customers.

        Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is
        enabled by default), projen will automatically add a dev dependency with a
        pinned version for each peer dependency. This will ensure that you build &
        test your module against the lowest peer version required.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("peer_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pnpm_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version of PNPM to use if using PNPM as a package manager.

        :default: "7"

        :stability: experimental
        '''
        result = self._values.get("pnpm_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''(experimental) The repository is the location where the actual code for your package lives.

        See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository

        :stability: experimental
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.

        :stability: experimental
        '''
        result = self._values.get("repository_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scoped_packages_options(
        self,
    ) -> typing.Optional[typing.List[_projen_javascript_04054675.ScopedPackagesOptions]]:
        '''(experimental) Options for privately hosted scoped packages.

        :default: - fetch all scoped packages from the public npm registry

        :stability: experimental
        '''
        result = self._values.get("scoped_packages_options")
        return typing.cast(typing.Optional[typing.List[_projen_javascript_04054675.ScopedPackagesOptions]], result)

    @builtins.property
    def scripts(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(deprecated) npm scripts to include.

        If a script has the same name as a standard script,
        the standard script will be overwritten.
        Also adds the script as a task.

        :default: {}

        :deprecated: use ``project.addTask()`` or ``package.setScript()``

        :stability: deprecated
        '''
        result = self._values.get("scripts")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def stability(self) -> typing.Optional[builtins.str]:
        '''(experimental) Package's Stability.

        :stability: experimental
        '''
        result = self._values.get("stability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jsii_release_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version requirement of ``publib`` which is used to publish modules to npm.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("jsii_release_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def major_version(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Major version to release from the default branch.

        If this is specified, we bump the latest version of this major version line.
        If not specified, we bump the global latest version.

        :default: - Major version is not enforced.

        :stability: experimental
        '''
        result = self._values.get("major_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_major_version(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Minimal Major version to release.

        This can be useful to set to 1, as breaking changes before the 1.x major
        release are not incrementing the major version number.

        Can not be set together with ``majorVersion``.

        :default: - No minimum version is being enforced

        :stability: experimental
        '''
        result = self._values.get("min_major_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def npm_dist_tag(self) -> typing.Optional[builtins.str]:
        '''(experimental) The npmDistTag to use when publishing from the default branch.

        To set the npm dist-tag for release branches, set the ``npmDistTag`` property
        for each branch.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("npm_dist_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def post_build_steps(
        self,
    ) -> typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]]:
        '''(experimental) Steps to execute after build as part of the release workflow.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("post_build_steps")
        return typing.cast(typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]], result)

    @builtins.property
    def prerelease(self) -> typing.Optional[builtins.str]:
        '''(experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre").

        :default: - normal semantic versions

        :stability: experimental
        '''
        result = self._values.get("prerelease")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publish_dry_run(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Instead of actually publishing to package managers, just print the publishing command.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("publish_dry_run")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def publish_tasks(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define publishing tasks that can be executed manually as well as workflows.

        Normally, publishing only happens within automated workflows. Enable this
        in order to create a publishing task for each publishing activity.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("publish_tasks")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_branches(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _projen_release_04054675.BranchOptions]]:
        '''(experimental) Defines additional release branches.

        A workflow will be created for each
        release branch which will publish releases from commits in this branch.
        Each release branch *must* be assigned a major version number which is used
        to enforce that versions published from that branch always use that major
        version. If multiple branches are used, the ``majorVersion`` field must also
        be provided for the default branch.

        :default:

        - no additional branches are used for release. you can use
        ``addBranch()`` to add additional branches.

        :stability: experimental
        '''
        result = self._values.get("release_branches")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _projen_release_04054675.BranchOptions]], result)

    @builtins.property
    def release_every_commit(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``.

        :default: true

        :deprecated: Use ``releaseTrigger: ReleaseTrigger.continuous()`` instead

        :stability: deprecated
        '''
        result = self._values.get("release_every_commit")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_failure_issue(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Create a github issue on every failed publishing task.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("release_failure_issue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_failure_issue_label(self) -> typing.Optional[builtins.str]:
        '''(experimental) The label to apply to issues indicating publish failures.

        Only applies if ``releaseFailureIssue`` is true.

        :default: "failed-release"

        :stability: experimental
        '''
        result = self._values.get("release_failure_issue_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_schedule(self) -> typing.Optional[builtins.str]:
        '''(deprecated) CRON schedule to trigger new releases.

        :default: - no scheduled releases

        :deprecated: Use ``releaseTrigger: ReleaseTrigger.scheduled()`` instead

        :stability: deprecated
        '''
        result = self._values.get("release_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_tag_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers.

        Note: this prefix is used to detect the latest tagged version
        when bumping, so if you change this on a project with an existing version
        history, you may need to manually tag your latest release
        with the new prefix.

        :default: "v"

        :stability: experimental
        '''
        result = self._values.get("release_tag_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_trigger(
        self,
    ) -> typing.Optional[_projen_release_04054675.ReleaseTrigger]:
        '''(experimental) The release trigger to use.

        :default: - Continuous releases (``ReleaseTrigger.continuous()``)

        :stability: experimental
        '''
        result = self._values.get("release_trigger")
        return typing.cast(typing.Optional[_projen_release_04054675.ReleaseTrigger], result)

    @builtins.property
    def release_workflow_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the default release workflow.

        :default: "Release"

        :stability: experimental
        '''
        result = self._values.get("release_workflow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_workflow_setup_steps(
        self,
    ) -> typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]]:
        '''(experimental) A set of workflow steps to execute in order to setup the workflow container.

        :stability: experimental
        '''
        result = self._values.get("release_workflow_setup_steps")
        return typing.cast(typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]], result)

    @builtins.property
    def versionrc_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Custom configuration used when creating changelog with standard-version package.

        Given values either append to default configuration or overwrite values in it.

        :default: - standard configuration applicable for GitHub repositories

        :stability: experimental
        '''
        result = self._values.get("versionrc_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def workflow_container_image(self) -> typing.Optional[builtins.str]:
        '''(experimental) Container image to use for GitHub workflows.

        :default: - default image

        :stability: experimental
        '''
        result = self._values.get("workflow_container_image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_runs_on(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Github Runner selection labels.

        :default: ["ubuntu-latest"]

        :stability: experimental
        '''
        result = self._values.get("workflow_runs_on")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def default_release_branch(self) -> builtins.str:
        '''(experimental) The name of the main release branch.

        :default: "main"

        :stability: experimental
        '''
        result = self._values.get("default_release_branch")
        assert result is not None, "Required property 'default_release_branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def artifacts_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) A directory which will contain build artifacts.

        :default: "dist"

        :stability: experimental
        '''
        result = self._values.get("artifacts_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_approve_upgrades(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued).

        Throw if set to true but ``autoApproveOptions`` are not defined.

        :default: - true

        :stability: experimental
        '''
        result = self._values.get("auto_approve_upgrades")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def build_workflow(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define a GitHub workflow for building PRs.

        :default: - true if not a subproject

        :stability: experimental
        '''
        result = self._values.get("build_workflow")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def build_workflow_triggers(
        self,
    ) -> typing.Optional[_projen_github_workflows_04054675.Triggers]:
        '''(experimental) Build workflow triggers.

        :default: "{ pullRequest: {}, workflowDispatch: {} }"

        :stability: experimental
        '''
        result = self._values.get("build_workflow_triggers")
        return typing.cast(typing.Optional[_projen_github_workflows_04054675.Triggers], result)

    @builtins.property
    def bundler_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.BundlerOptions]:
        '''(experimental) Options for ``Bundler``.

        :stability: experimental
        '''
        result = self._values.get("bundler_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.BundlerOptions], result)

    @builtins.property
    def code_cov(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v3 A secret is required for private repos. Configured with @codeCovTokenSecret.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("code_cov")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def code_cov_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories.

        :default: - if this option is not specified, only public repositories are supported

        :stability: experimental
        '''
        result = self._values.get("code_cov_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copyright_owner(self) -> typing.Optional[builtins.str]:
        '''(experimental) License copyright owner.

        :default: - defaults to the value of authorName or "" if ``authorName`` is undefined.

        :stability: experimental
        '''
        result = self._values.get("copyright_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copyright_period(self) -> typing.Optional[builtins.str]:
        '''(experimental) The copyright years to put in the LICENSE file.

        :default: - current year

        :stability: experimental
        '''
        result = self._values.get("copyright_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dependabot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use dependabot to handle dependency upgrades.

        Cannot be used in conjunction with ``depsUpgrade``.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dependabot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dependabot_options(
        self,
    ) -> typing.Optional[_projen_github_04054675.DependabotOptions]:
        '''(experimental) Options for dependabot.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("dependabot_options")
        return typing.cast(typing.Optional[_projen_github_04054675.DependabotOptions], result)

    @builtins.property
    def deps_upgrade(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use github workflows to handle dependency upgrades.

        Cannot be used in conjunction with ``dependabot``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("deps_upgrade")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deps_upgrade_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.UpgradeDependenciesOptions]:
        '''(experimental) Options for ``UpgradeDependencies``.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("deps_upgrade_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.UpgradeDependenciesOptions], result)

    @builtins.property
    def gitignore(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Additional entries to .gitignore.

        :stability: experimental
        '''
        result = self._values.get("gitignore")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def jest(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup jest unit tests.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("jest")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def jest_options(self) -> typing.Optional[_projen_javascript_04054675.JestOptions]:
        '''(experimental) Jest options.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("jest_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.JestOptions], result)

    @builtins.property
    def mutable_build(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically update files modified during builds to pull-request branches.

        This means
        that any files synthesized by projen or e.g. test snapshots will always be up-to-date
        before a PR is merged.

        Implies that PR builds do not have anti-tamper checks.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("mutable_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def npmignore(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) Additional entries to .npmignore.

        :deprecated: - use ``project.addPackageIgnore``

        :stability: deprecated
        '''
        result = self._values.get("npmignore")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def npmignore_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("npmignore_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def npm_ignore_options(self) -> typing.Optional[_projen_04054675.IgnoreFileOptions]:
        '''(experimental) Configuration options for .npmignore file.

        :stability: experimental
        '''
        result = self._values.get("npm_ignore_options")
        return typing.cast(typing.Optional[_projen_04054675.IgnoreFileOptions], result)

    @builtins.property
    def package(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``).

        :default: true

        :stability: experimental
        '''
        result = self._values.get("package")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def prettier(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup prettier.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("prettier")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def prettier_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.PrettierOptions]:
        '''(experimental) Prettier options.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("prettier_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.PrettierOptions], result)

    @builtins.property
    def projen_dev_dependency(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates of "projen" should be installed as a devDependency.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("projen_dev_dependency")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_js(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation.

        :default: - true if projenrcJson is false

        :stability: experimental
        '''
        result = self._values.get("projenrc_js")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_js_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.js.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_js_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.ProjenrcOptions], result)

    @builtins.property
    def projen_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version of projen to install.

        :default: - Defaults to the latest version.

        :stability: experimental
        '''
        result = self._values.get("projen_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_request_template(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include a GitHub pull request template.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("pull_request_template")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pull_request_template_contents(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The contents of the pull request template.

        :default: - default content

        :stability: experimental
        '''
        result = self._values.get("pull_request_template_contents")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def release(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add release management to this project.

        :default: - true (false for subprojects)

        :stability: experimental
        '''
        result = self._values.get("release")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_to_npm(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically release to npm when new versions are introduced.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("release_to_npm")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_workflow(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) DEPRECATED: renamed to ``release``.

        :default: - true if not a subproject

        :deprecated: see ``release``.

        :stability: deprecated
        '''
        result = self._values.get("release_workflow")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def workflow_bootstrap_steps(
        self,
    ) -> typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]]:
        '''(experimental) Workflow steps to use in order to bootstrap this repo.

        :default: "yarn install --frozen-lockfile && yarn projen"

        :stability: experimental
        '''
        result = self._values.get("workflow_bootstrap_steps")
        return typing.cast(typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]], result)

    @builtins.property
    def workflow_git_identity(
        self,
    ) -> typing.Optional[_projen_github_04054675.GitIdentity]:
        '''(experimental) The git identity to use in workflows.

        :default: - GitHub Actions

        :stability: experimental
        '''
        result = self._values.get("workflow_git_identity")
        return typing.cast(typing.Optional[_projen_github_04054675.GitIdentity], result)

    @builtins.property
    def workflow_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The node version to use in GitHub workflows.

        :default: - same as ``minNodeVersion``

        :stability: experimental
        '''
        result = self._values.get("workflow_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_tsconfig(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("disable_tsconfig")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def disable_tsconfig_dev(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Do not generate a ``tsconfig.dev.json`` file.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("disable_tsconfig_dev")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def docgen(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Docgen by Typedoc.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("docgen")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def docs_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) Docs directory.

        :default: "docs"

        :stability: experimental
        '''
        result = self._values.get("docs_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entrypoint_types(self) -> typing.Optional[builtins.str]:
        '''(experimental) The .d.ts file that includes the type declarations for this module.

        :default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)

        :stability: experimental
        '''
        result = self._values.get("entrypoint_types")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eslint(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup eslint.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("eslint")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def eslint_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.EslintOptions]:
        '''(experimental) Eslint options.

        :default: - opinionated default options

        :stability: experimental
        '''
        result = self._values.get("eslint_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.EslintOptions], result)

    @builtins.property
    def libdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Typescript  artifacts output directory.

        :default: "lib"

        :stability: experimental
        '''
        result = self._values.get("libdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projenrc_ts(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use TypeScript for your projenrc file (``.projenrc.ts``).

        :default: false

        :stability: experimental
        :pjnew: true
        '''
        result = self._values.get("projenrc_ts")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_ts_options(
        self,
    ) -> typing.Optional[_projen_typescript_04054675.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.ts.

        :stability: experimental
        '''
        result = self._values.get("projenrc_ts_options")
        return typing.cast(typing.Optional[_projen_typescript_04054675.ProjenrcOptions], result)

    @builtins.property
    def sample_code(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("sample_code")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def srcdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Typescript sources directory.

        :default: "src"

        :stability: experimental
        '''
        result = self._values.get("srcdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def testdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``.

        If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``),
        then tests are going to be compiled into ``lib/`` and executed as javascript.
        If the test directory is outside of ``src``, then we configure jest to
        compile the code in-memory.

        :default: "test"

        :stability: experimental
        '''
        result = self._values.get("testdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tsconfig(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.TypescriptConfigOptions]:
        '''(experimental) Custom TSConfig.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("tsconfig")
        return typing.cast(typing.Optional[_projen_javascript_04054675.TypescriptConfigOptions], result)

    @builtins.property
    def tsconfig_dev(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.TypescriptConfigOptions]:
        '''(experimental) Custom tsconfig options for the development tsconfig.json file (used for testing).

        :default: - use the production tsconfig options

        :stability: experimental
        '''
        result = self._values.get("tsconfig_dev")
        return typing.cast(typing.Optional[_projen_javascript_04054675.TypescriptConfigOptions], result)

    @builtins.property
    def tsconfig_dev_file(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the development tsconfig.json file.

        :default: "tsconfig.dev.json"

        :stability: experimental
        '''
        result = self._values.get("tsconfig_dev_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def typescript_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) TypeScript version to use.

        NOTE: Typescript is not semantically versioned and should remain on the
        same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``).

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("typescript_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def monorepo_upgrade_deps(self) -> typing.Optional[builtins.bool]:
        '''Whether to include an upgrade-deps task at the root of the monorepo which will upgrade all dependencies.

        :default: true
        '''
        result = self._values.get("monorepo_upgrade_deps")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def monorepo_upgrade_deps_options(
        self,
    ) -> typing.Optional[MonorepoUpgradeDepsOptions]:
        '''Monorepo Upgrade Deps options.

        This is only used if monorepoUpgradeDeps is true.

        :default: undefined
        '''
        result = self._values.get("monorepo_upgrade_deps_options")
        return typing.cast(typing.Optional[MonorepoUpgradeDepsOptions], result)

    @builtins.property
    def workspace_config(self) -> typing.Optional["WorkspaceConfig"]:
        '''Configuration for workspace.'''
        result = self._values.get("workspace_config")
        return typing.cast(typing.Optional["WorkspaceConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NxMonorepoProjectOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NxProject(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/nx-monorepo.NxProject",
):
    '''(experimental) Component which manages the project specific NX Config and is added to all NXMonorepo subprojects.

    :stability: experimental
    '''

    def __init__(self, project: _projen_04054675.Project) -> None:
        '''
        :param project: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f9b6741626fc389be079ffde07106d406606b361d760b9d6f5999b8739c6718)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        jsii.create(self.__class__, self, [project])

    @jsii.member(jsii_name="ensure")
    @builtins.classmethod
    def ensure(cls, project: _projen_04054675.Project) -> "NxProject":
        '''(experimental) Retrieves an instance of NXProject if one is associated to the given project, otherwise created a NXProject instance for the project.

        :param project: project instance.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80dc1deed56597718342c982e8e5c8b9441ff9f326ef7b3a55d7139fe335075e)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        return typing.cast("NxProject", jsii.sinvoke(cls, "ensure", [project]))

    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(cls, project: _projen_04054675.Project) -> typing.Optional["NxProject"]:
        '''(experimental) Retrieves an instance of NXProject if one is associated to the given project.

        :param project: project instance.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a76cd792862733ce23cd71fa357bc8e4765d27391214e2477052d22cdd70cfdc)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        return typing.cast(typing.Optional["NxProject"], jsii.sinvoke(cls, "of", [project]))

    @jsii.member(jsii_name="addBuildTargetFiles")
    def add_build_target_files(
        self,
        inputs: typing.Optional[typing.Sequence[typing.Union[builtins.str, _IInput_844dcc6a]]] = None,
        outputs: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Add input and output files to build target.

        :param inputs: Input files.
        :param outputs: Output files.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7694f119757945af275fa1da6a98d29767ad632e77c40c6659cc3fa52f7f967a)
            check_type(argname="argument inputs", value=inputs, expected_type=type_hints["inputs"])
            check_type(argname="argument outputs", value=outputs, expected_type=type_hints["outputs"])
        return typing.cast(None, jsii.invoke(self, "addBuildTargetFiles", [inputs, outputs]))

    @jsii.member(jsii_name="addImplicitDependency")
    def add_implicit_dependency(
        self,
        *dependee: typing.Union[builtins.str, _projen_04054675.Project],
    ) -> None:
        '''(experimental) Adds an implicit dependency between the dependant (this project) and dependee.

        :param dependee: project to add the implicit dependency on.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18df3f20897c99ed81405d7cb6bf1319f9a33d702d599b746dba5e9445d58799)
            check_type(argname="argument dependee", value=dependee, expected_type=typing.Tuple[type_hints["dependee"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(None, jsii.invoke(self, "addImplicitDependency", [*dependee]))

    @jsii.member(jsii_name="addTag")
    def add_tag(self, *tags: builtins.str) -> None:
        '''(experimental) Add tag.

        :param tags: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1fc0c6d4ed48fa6b591c2f6eb760d1a105804c8b2977d7c4a1bd7383ad62e91)
            check_type(argname="argument tags", value=tags, expected_type=typing.Tuple[type_hints["tags"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(None, jsii.invoke(self, "addTag", [*tags]))

    @jsii.member(jsii_name="inferTargets")
    def infer_targets(self) -> None:
        '''(experimental) Automatically infer targets based on project type.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "inferTargets", []))

    @jsii.member(jsii_name="merge")
    def merge(
        self,
        *,
        implicit_dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        included_scripts: typing.Optional[typing.Sequence[builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        named_inputs: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
        root: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        targets: typing.Optional[typing.Mapping[builtins.str, _IProjectTarget_963c071e]] = None,
    ) -> None:
        '''(experimental) Merge configuration into existing config.

        :param implicit_dependencies: Implicit dependencies.
        :param included_scripts: Explicit list of scripts for Nx to include.
        :param name: Name of project.
        :param named_inputs: Named inputs.
        :param root: Project root dir path relative to workspace.
        :param tags: Project tag annotations.
        :param targets: Targets configuration.

        :stability: experimental
        '''
        config = _ProjectConfig_a9302870(
            implicit_dependencies=implicit_dependencies,
            included_scripts=included_scripts,
            name=name,
            named_inputs=named_inputs,
            root=root,
            tags=tags,
            targets=targets,
        )

        return typing.cast(None, jsii.invoke(self, "merge", [config]))

    @jsii.member(jsii_name="setNamedInput")
    def set_named_input(
        self,
        name: builtins.str,
        inputs: typing.Sequence[builtins.str],
    ) -> None:
        '''(experimental) Set ``namedInputs`` helper.

        :param name: -
        :param inputs: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4135c80ab345edf257a40519f470c3698ab321d47d413e88d471fddec266f302)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument inputs", value=inputs, expected_type=type_hints["inputs"])
        return typing.cast(None, jsii.invoke(self, "setNamedInput", [name, inputs]))

    @jsii.member(jsii_name="setTarget")
    def set_target(
        self,
        name: builtins.str,
        target: _IProjectTarget_963c071e,
        include_defaults: typing.Optional[typing.Union[builtins.str, builtins.bool]] = None,
    ) -> None:
        '''(experimental) Set ``targets`` helper.

        :param name: -
        :param target: -
        :param include_defaults: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4e6a22faad472bc3a01a88944455bdc78694211a9a3ab8e3f768277b7fa22f2)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument include_defaults", value=include_defaults, expected_type=type_hints["include_defaults"])
        return typing.cast(None, jsii.invoke(self, "setTarget", [name, target, include_defaults]))

    @jsii.member(jsii_name="synthesize")
    def synthesize(self) -> None:
        '''(experimental) Synthesizes files to the project output directory.

        :stability: experimental
        :interface: true
        '''
        return typing.cast(None, jsii.invoke(self, "synthesize", []))

    @builtins.property
    @jsii.member(jsii_name="file")
    def file(self) -> _projen_04054675.JsonFile:
        '''(experimental) Raw json file.

        **Attention:** any overrides applied here will not be visible
        in the properties and only included in final synthesized output,
        and likely to override native handling.

        :stability: experimental
        :advanced: true
        '''
        return typing.cast(_projen_04054675.JsonFile, jsii.get(self, "file"))

    @builtins.property
    @jsii.member(jsii_name="implicitDependencies")
    def implicit_dependencies(self) -> typing.List[builtins.str]:
        '''(experimental) Implicit dependencies.

        :see: https://nx.dev/reference/project-configuration#implicitdependencies
        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "implicitDependencies"))

    @implicit_dependencies.setter
    def implicit_dependencies(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2c6413f97fd812c8d2c8c962df57749ff79c358f69af1d71f4bb6627a447e37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "implicitDependencies", value)

    @builtins.property
    @jsii.member(jsii_name="includedScripts")
    def included_scripts(self) -> typing.List[builtins.str]:
        '''(experimental) Explicit list of scripts for Nx to include.

        :see: https://nx.dev/reference/project-configuration#ignoring-package.json-scripts
        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "includedScripts"))

    @included_scripts.setter
    def included_scripts(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d01a4a451fc5f546fd1873c4ba364ee7d223dcf21e9266eba6f234211d36f59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includedScripts", value)

    @builtins.property
    @jsii.member(jsii_name="namedInputs")
    def named_inputs(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''(experimental) Named inputs.

        :see: https://nx.dev/reference/nx-json#inputs-&-namedinputs
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "namedInputs"))

    @named_inputs.setter
    def named_inputs(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0979a49c05bce24f7c99794ecd4f290be7cce1322a60a051955879f975f320d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namedInputs", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        '''(experimental) Project tag annotations.

        :see: https://nx.dev/reference/project-configuration#tags
        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__351c7334d1c7664fa8507a5bad91a7f4439f997a77d08c51539a48105f86163f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targets")
    def targets(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''(experimental) Targets configuration.

        :see: https://nx.dev/reference/project-configuration
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "targets"))

    @targets.setter
    def targets(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cae678f0f69ee19577586deaa478e15f1288bbca4f599787c8f71aec317be950)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targets", value)


class NxWorkspace(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/nx-monorepo.NxWorkspace",
):
    '''(experimental) Component which manages the workspace specific NX Config for the root monorepo.

    :stability: experimental
    '''

    def __init__(self, project: _projen_04054675.Project) -> None:
        '''
        :param project: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8386594efa8f970e49738559198399eea321b2a199064942362bb1564030f7e)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        jsii.create(self.__class__, self, [project])

    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(cls, scope: _projen_04054675.Project) -> typing.Optional["NxWorkspace"]:
        '''(experimental) Retrieves the singleton instance associated with project root.

        :param scope: project instance.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__695644f0eecd1924376627c1424be5f5a140237381933295f1e80f7a07f145a9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(typing.Optional["NxWorkspace"], jsii.sinvoke(cls, "of", [scope]))

    @jsii.member(jsii_name="preSynthesize")
    def pre_synthesize(self) -> None:
        '''(experimental) Called before synthesis.

        :stability: experimental
        :inheritdoc: true
        '''
        return typing.cast(None, jsii.invoke(self, "preSynthesize", []))

    @jsii.member(jsii_name="setNamedInput")
    def set_named_input(
        self,
        name: builtins.str,
        inputs: typing.Sequence[builtins.str],
    ) -> None:
        '''(experimental) Set ``namedInput`` value helper.

        :param name: -
        :param inputs: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__802546f32bcb961dc69a40dec5fc86f113597e7a893d1f2a6a3937fd36c5c982)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument inputs", value=inputs, expected_type=type_hints["inputs"])
        return typing.cast(None, jsii.invoke(self, "setNamedInput", [name, inputs]))

    @jsii.member(jsii_name="setTargetDefault")
    def set_target_default(
        self,
        name: builtins.str,
        target: _IProjectTarget_963c071e,
        merge: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Set ``targetDefaults`` helper.

        :param name: -
        :param target: -
        :param merge: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15b0bbfb5d798c8113892ba448ed658f91d8ffa282270fafee136f9a84b94fa8)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument merge", value=merge, expected_type=type_hints["merge"])
        return typing.cast(None, jsii.invoke(self, "setTargetDefault", [name, target, merge]))

    @jsii.member(jsii_name="synthesize")
    def synthesize(self) -> None:
        '''(experimental) Synthesizes files to the project output directory.

        :stability: experimental
        :inheritdoc: true
        '''
        return typing.cast(None, jsii.invoke(self, "synthesize", []))

    @jsii.member(jsii_name="useNxCloud")
    def use_nx_cloud(self, read_only_access_token: builtins.str) -> None:
        '''(experimental) Setup workspace to use nx-cloud.

        :param read_only_access_token: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3395df127f6804ff001c56fd57148403ff9293019d38cfdbbacf8a93964efb65)
            check_type(argname="argument read_only_access_token", value=read_only_access_token, expected_type=type_hints["read_only_access_token"])
        return typing.cast(None, jsii.invoke(self, "useNxCloud", [read_only_access_token]))

    @builtins.property
    @jsii.member(jsii_name="nxIgnore")
    def nx_ignore(self) -> _projen_04054675.IgnoreFile:
        '''(experimental) .nxignore file.

        :stability: experimental
        '''
        return typing.cast(_projen_04054675.IgnoreFile, jsii.get(self, "nxIgnore"))

    @builtins.property
    @jsii.member(jsii_name="nxJson")
    def nx_json(self) -> _projen_04054675.JsonFile:
        '''(experimental) Raw nx.json file to support overrides that aren't handled directly.

        **Attention:** any overrides applied here will not be visible
        in the properties and only included in final synthesized output,
        and likely to override native handling.

        :stability: experimental
        :advanced: true
        '''
        return typing.cast(_projen_04054675.JsonFile, jsii.get(self, "nxJson"))

    @builtins.property
    @jsii.member(jsii_name="affected")
    def affected(self) -> _INxAffectedConfig_f6105638:
        '''(experimental) Default options for ``nx affected``.

        :stability: experimental
        '''
        return typing.cast(_INxAffectedConfig_f6105638, jsii.get(self, "affected"))

    @affected.setter
    def affected(self, value: _INxAffectedConfig_f6105638) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1abb24d49fe05a58d9f5daed9e2ce6ac2e746bbfc7bdbc00aa0c71f94f21958)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "affected", value)

    @builtins.property
    @jsii.member(jsii_name="autoInferProjectTargets")
    def auto_infer_project_targets(self) -> builtins.bool:
        '''(experimental) Automatically infer NxProject targets based on project type.

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "autoInferProjectTargets"))

    @auto_infer_project_targets.setter
    def auto_infer_project_targets(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64c689a104fb9ab2e1616db76edf6882af8d61e9ed6fcaff155d15aaf50c652c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoInferProjectTargets", value)

    @builtins.property
    @jsii.member(jsii_name="cacheableOperations")
    def cacheable_operations(self) -> typing.List[builtins.str]:
        '''(experimental) List of cacheable operations.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "cacheableOperations"))

    @cacheable_operations.setter
    def cacheable_operations(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b54df1d7b0ed7e22d17c869119f1ef6fafe6e360e2cd0ead989d8659553f301a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cacheableOperations", value)

    @builtins.property
    @jsii.member(jsii_name="defaultTaskRunner")
    def default_task_runner(self) -> builtins.str:
        '''(experimental) Default task runner.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "defaultTaskRunner"))

    @default_task_runner.setter
    def default_task_runner(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ee103672ffd4c42450f81e2b90a8a181a17ab55e52bff2e270a3bc944389a4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultTaskRunner", value)

    @builtins.property
    @jsii.member(jsii_name="defaultTaskRunnerOptions")
    def default_task_runner_options(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''(experimental) Default task runner options.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "defaultTaskRunnerOptions"))

    @default_task_runner_options.setter
    def default_task_runner_options(
        self,
        value: typing.Mapping[builtins.str, typing.Any],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a893b1a3babbb835b1a6cda09d9bd1e1c5907924715be1770d1289e25d99946)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultTaskRunnerOptions", value)

    @builtins.property
    @jsii.member(jsii_name="extends")
    def extends(self) -> builtins.str:
        '''(experimental) Some presets use the extends property to hide some default options in a separate json file.

        The json file specified in the extends property is located in your node_modules folder.
        The Nx preset files are specified in the nx package.

        :default: "nx/presets/npm.json"

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "extends"))

    @extends.setter
    def extends(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a37d2f6ad8dbec05d4efad5e60e6c7ea9150a5b177d62493477b0fc78b12cca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extends", value)

    @builtins.property
    @jsii.member(jsii_name="namedInputs")
    def named_inputs(self) -> typing.Mapping[builtins.str, typing.List[builtins.str]]:
        '''(experimental) Named inputs.

        :see: https://nx.dev/reference/nx-json#inputs-&-namedinputs
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.List[builtins.str]], jsii.get(self, "namedInputs"))

    @named_inputs.setter
    def named_inputs(
        self,
        value: typing.Mapping[builtins.str, typing.List[builtins.str]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06d365fd7564cdcc6b94e99732313d1713798c21094146651be691e459863f71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namedInputs", value)

    @builtins.property
    @jsii.member(jsii_name="nonNativeHasher")
    def non_native_hasher(self) -> builtins.bool:
        '''(experimental) Indicates if non-native nx hasher will be used.

        If true, the NX_NON_NATIVE_HASHER env var will be set
        to true for all project tasks.

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "nonNativeHasher"))

    @non_native_hasher.setter
    def non_native_hasher(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__119f31ba008edd00434e5b3f549fb6a094866bd2470957d2d227d69a8cc8ce8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nonNativeHasher", value)

    @builtins.property
    @jsii.member(jsii_name="npmScope")
    def npm_scope(self) -> builtins.str:
        '''(experimental) Tells Nx what prefix to use when generating library imports.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "npmScope"))

    @npm_scope.setter
    def npm_scope(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__358d9f024d09e37b4537491c2dcf8f7a13c0f036968bde12f7b91c6119e96b09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "npmScope", value)

    @builtins.property
    @jsii.member(jsii_name="plugins")
    def plugins(self) -> typing.List[builtins.str]:
        '''(experimental) Plugins for extending the project graph.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "plugins"))

    @plugins.setter
    def plugins(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9097f9c3bcd4b178a1ca6b32ca26843cea639c347870a0fb6e8cbd48f49e5823)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "plugins", value)

    @builtins.property
    @jsii.member(jsii_name="pluginsConfig")
    def plugins_config(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''(experimental) Configuration for Nx Plugins.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "pluginsConfig"))

    @plugins_config.setter
    def plugins_config(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ce38c34ab569ebd21cb5108a33114f99224a7285f5054bfad9938a82c9b840b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pluginsConfig", value)

    @builtins.property
    @jsii.member(jsii_name="targetDefaults")
    def target_defaults(self) -> typing.Mapping[builtins.str, _IProjectTarget_963c071e]:
        '''(experimental) Dependencies between different target names across all projects.

        :see: https://nx.dev/reference/nx-json#target-defaults
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, _IProjectTarget_963c071e], jsii.get(self, "targetDefaults"))

    @target_defaults.setter
    def target_defaults(
        self,
        value: typing.Mapping[builtins.str, _IProjectTarget_963c071e],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af4651413cd46bdb50c4e4b9c13afa04f3a15bf16da8d963fc6a6b364e19aa4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetDefaults", value)

    @builtins.property
    @jsii.member(jsii_name="tasksRunnerOptions")
    def tasks_runner_options(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''(experimental) Task runner options.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "tasksRunnerOptions"))

    @tasks_runner_options.setter
    def tasks_runner_options(
        self,
        value: typing.Mapping[builtins.str, typing.Any],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a6d1c0b12954870f9022d8b0eb06bbb24e16d62a2cdfc0ca41630f3ae2e3352)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tasksRunnerOptions", value)

    @builtins.property
    @jsii.member(jsii_name="cacheDirectory")
    def cache_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) Override the default nx cacheDirectory.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cacheDirectory"))

    @cache_directory.setter
    def cache_directory(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa4ffd9f7ecea4596de010cb12bb45325114e74f5bb90543d1b5556fd723a59f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cacheDirectory", value)

    @builtins.property
    @jsii.member(jsii_name="workspaceLayout")
    def workspace_layout(self) -> typing.Optional[_IWorkspaceLayout_91f3d180]:
        '''(experimental) Where new apps + libs should be placed.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_IWorkspaceLayout_91f3d180], jsii.get(self, "workspaceLayout"))

    @workspace_layout.setter
    def workspace_layout(
        self,
        value: typing.Optional[_IWorkspaceLayout_91f3d180],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af52b1df34ba2dfccaa7543a6a4a262e81ddbe95c35b8f17c283f21c9a361bc1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceLayout", value)


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/nx-monorepo.SemverGroup",
    jsii_struct_bases=[],
    name_mapping={
        "dependencies": "dependencies",
        "packages": "packages",
        "range": "range",
        "dependency_types": "dependencyTypes",
    },
)
class SemverGroup:
    def __init__(
        self,
        *,
        dependencies: typing.Sequence[builtins.str],
        packages: typing.Sequence[builtins.str],
        range: builtins.str,
        dependency_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param dependencies: the names of the dependencies (eg. "lodash") which belong to this group
        :param packages: the names of packages in your monorepo which belong to this group, taken from the "name" field in package.json, not the package directory name.
        :param range: the semver range which dependencies in this group should use.
        :param dependency_types: optionally only apply this group to dependencies of the provided types.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c17c85363fc4b46a5bdccfd298a080815f6cec752f651ba4183f84a542d398b3)
            check_type(argname="argument dependencies", value=dependencies, expected_type=type_hints["dependencies"])
            check_type(argname="argument packages", value=packages, expected_type=type_hints["packages"])
            check_type(argname="argument range", value=range, expected_type=type_hints["range"])
            check_type(argname="argument dependency_types", value=dependency_types, expected_type=type_hints["dependency_types"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "dependencies": dependencies,
            "packages": packages,
            "range": range,
        }
        if dependency_types is not None:
            self._values["dependency_types"] = dependency_types

    @builtins.property
    def dependencies(self) -> typing.List[builtins.str]:
        '''the names of the dependencies (eg.

        "lodash") which belong to this group
        '''
        result = self._values.get("dependencies")
        assert result is not None, "Required property 'dependencies' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def packages(self) -> typing.List[builtins.str]:
        '''the names of packages in your monorepo which belong to this group, taken from the "name" field in package.json, not the package directory name.'''
        result = self._values.get("packages")
        assert result is not None, "Required property 'packages' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def range(self) -> builtins.str:
        '''the semver range which dependencies in this group should use.'''
        result = self._values.get("range")
        assert result is not None, "Required property 'range' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dependency_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''optionally only apply this group to dependencies of the provided types.'''
        result = self._values.get("dependency_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SemverGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/nx-monorepo.SyncpackConfig",
    jsii_struct_bases=[],
    name_mapping={
        "dependency_types": "dependencyTypes",
        "dev": "dev",
        "filter": "filter",
        "indent": "indent",
        "overrides": "overrides",
        "peer": "peer",
        "pnpm_overrides": "pnpmOverrides",
        "prod": "prod",
        "resolutions": "resolutions",
        "semver_groups": "semverGroups",
        "semver_range": "semverRange",
        "sort_az": "sortAz",
        "sort_first": "sortFirst",
        "source": "source",
        "version_groups": "versionGroups",
        "workspace": "workspace",
    },
)
class SyncpackConfig:
    def __init__(
        self,
        *,
        dependency_types: typing.Sequence[builtins.str],
        dev: builtins.bool,
        filter: builtins.str,
        indent: builtins.str,
        overrides: builtins.bool,
        peer: builtins.bool,
        pnpm_overrides: builtins.bool,
        prod: builtins.bool,
        resolutions: builtins.bool,
        semver_groups: typing.Sequence[typing.Union[SemverGroup, typing.Dict[builtins.str, typing.Any]]],
        semver_range: builtins.str,
        sort_az: typing.Sequence[builtins.str],
        sort_first: typing.Sequence[builtins.str],
        source: typing.Sequence[builtins.str],
        version_groups: typing.Sequence[typing.Union["VersionGroup", typing.Dict[builtins.str, typing.Any]]],
        workspace: builtins.bool,
    ) -> None:
        '''
        :param dependency_types: which dependency properties to search within.
        :param dev: whether to search within devDependencies.
        :param filter: a string which will be passed to ``new RegExp()`` to match against package names that should be included.
        :param indent: the character(s) to be used to indent your package.json files when writing to disk.
        :param overrides: whether to search within npm overrides.
        :param peer: whether to search within peerDependencies.
        :param pnpm_overrides: whether to search within pnpm overrides.
        :param prod: whether to search within dependencies.
        :param resolutions: whether to search within yarn resolutions.
        :param semver_groups: 
        :param semver_range: defaults to ``""`` to ensure that exact dependency versions are used instead of loose ranges.
        :param sort_az: which fields within package.json files should be sorted alphabetically.
        :param sort_first: which fields within package.json files should appear at the top, and in what order.
        :param source: glob patterns for package.json file locations.
        :param version_groups: 
        :param workspace: whether to include the versions of the ``--source`` packages developed in your workspace/monorepo as part of the search for versions to sync.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb223affa13a00894ad326c57270f418883297270633ef343c4dfdb409de6995)
            check_type(argname="argument dependency_types", value=dependency_types, expected_type=type_hints["dependency_types"])
            check_type(argname="argument dev", value=dev, expected_type=type_hints["dev"])
            check_type(argname="argument filter", value=filter, expected_type=type_hints["filter"])
            check_type(argname="argument indent", value=indent, expected_type=type_hints["indent"])
            check_type(argname="argument overrides", value=overrides, expected_type=type_hints["overrides"])
            check_type(argname="argument peer", value=peer, expected_type=type_hints["peer"])
            check_type(argname="argument pnpm_overrides", value=pnpm_overrides, expected_type=type_hints["pnpm_overrides"])
            check_type(argname="argument prod", value=prod, expected_type=type_hints["prod"])
            check_type(argname="argument resolutions", value=resolutions, expected_type=type_hints["resolutions"])
            check_type(argname="argument semver_groups", value=semver_groups, expected_type=type_hints["semver_groups"])
            check_type(argname="argument semver_range", value=semver_range, expected_type=type_hints["semver_range"])
            check_type(argname="argument sort_az", value=sort_az, expected_type=type_hints["sort_az"])
            check_type(argname="argument sort_first", value=sort_first, expected_type=type_hints["sort_first"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument version_groups", value=version_groups, expected_type=type_hints["version_groups"])
            check_type(argname="argument workspace", value=workspace, expected_type=type_hints["workspace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "dependency_types": dependency_types,
            "dev": dev,
            "filter": filter,
            "indent": indent,
            "overrides": overrides,
            "peer": peer,
            "pnpm_overrides": pnpm_overrides,
            "prod": prod,
            "resolutions": resolutions,
            "semver_groups": semver_groups,
            "semver_range": semver_range,
            "sort_az": sort_az,
            "sort_first": sort_first,
            "source": source,
            "version_groups": version_groups,
            "workspace": workspace,
        }

    @builtins.property
    def dependency_types(self) -> typing.List[builtins.str]:
        '''which dependency properties to search within.'''
        result = self._values.get("dependency_types")
        assert result is not None, "Required property 'dependency_types' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def dev(self) -> builtins.bool:
        '''whether to search within devDependencies.'''
        result = self._values.get("dev")
        assert result is not None, "Required property 'dev' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def filter(self) -> builtins.str:
        '''a string which will be passed to ``new RegExp()`` to match against package names that should be included.'''
        result = self._values.get("filter")
        assert result is not None, "Required property 'filter' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def indent(self) -> builtins.str:
        '''the character(s) to be used to indent your package.json files when writing to disk.'''
        result = self._values.get("indent")
        assert result is not None, "Required property 'indent' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def overrides(self) -> builtins.bool:
        '''whether to search within npm overrides.'''
        result = self._values.get("overrides")
        assert result is not None, "Required property 'overrides' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def peer(self) -> builtins.bool:
        '''whether to search within peerDependencies.'''
        result = self._values.get("peer")
        assert result is not None, "Required property 'peer' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def pnpm_overrides(self) -> builtins.bool:
        '''whether to search within pnpm overrides.'''
        result = self._values.get("pnpm_overrides")
        assert result is not None, "Required property 'pnpm_overrides' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def prod(self) -> builtins.bool:
        '''whether to search within dependencies.'''
        result = self._values.get("prod")
        assert result is not None, "Required property 'prod' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def resolutions(self) -> builtins.bool:
        '''whether to search within yarn resolutions.'''
        result = self._values.get("resolutions")
        assert result is not None, "Required property 'resolutions' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def semver_groups(self) -> typing.List[SemverGroup]:
        result = self._values.get("semver_groups")
        assert result is not None, "Required property 'semver_groups' is missing"
        return typing.cast(typing.List[SemverGroup], result)

    @builtins.property
    def semver_range(self) -> builtins.str:
        '''defaults to ``""`` to ensure that exact dependency versions are used instead of loose ranges.'''
        result = self._values.get("semver_range")
        assert result is not None, "Required property 'semver_range' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sort_az(self) -> typing.List[builtins.str]:
        '''which fields within package.json files should be sorted alphabetically.'''
        result = self._values.get("sort_az")
        assert result is not None, "Required property 'sort_az' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def sort_first(self) -> typing.List[builtins.str]:
        '''which fields within package.json files should appear at the top, and in what order.'''
        result = self._values.get("sort_first")
        assert result is not None, "Required property 'sort_first' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def source(self) -> typing.List[builtins.str]:
        '''glob patterns for package.json file locations.'''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def version_groups(self) -> typing.List["VersionGroup"]:
        result = self._values.get("version_groups")
        assert result is not None, "Required property 'version_groups' is missing"
        return typing.cast(typing.List["VersionGroup"], result)

    @builtins.property
    def workspace(self) -> builtins.bool:
        '''whether to include the versions of the ``--source`` packages developed in your workspace/monorepo as part of the search for versions to sync.'''
        result = self._values.get("workspace")
        assert result is not None, "Required property 'workspace' is missing"
        return typing.cast(builtins.bool, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SyncpackConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/nx-monorepo.VersionGroup",
    jsii_struct_bases=[],
    name_mapping={
        "dependencies": "dependencies",
        "packages": "packages",
        "dependency_types": "dependencyTypes",
        "is_banned": "isBanned",
        "pin_version": "pinVersion",
    },
)
class VersionGroup:
    def __init__(
        self,
        *,
        dependencies: typing.Sequence[builtins.str],
        packages: typing.Sequence[builtins.str],
        dependency_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        is_banned: typing.Optional[builtins.bool] = None,
        pin_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dependencies: the names of the dependencies (eg. "lodash") which belong to this group
        :param packages: the names of packages in your monorepo which belong to this group, taken from the "name" field in package.json, not the package directory name.
        :param dependency_types: optionally only apply this group to dependencies of the provided types.
        :param is_banned: optionally force all dependencies in this group to be removed.
        :param pin_version: optionally force all dependencies in this group to have this version.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d36097d2d6d9a3f5db57da121c324aa1a4c90571bf11d93a2e34f0a5b3f28966)
            check_type(argname="argument dependencies", value=dependencies, expected_type=type_hints["dependencies"])
            check_type(argname="argument packages", value=packages, expected_type=type_hints["packages"])
            check_type(argname="argument dependency_types", value=dependency_types, expected_type=type_hints["dependency_types"])
            check_type(argname="argument is_banned", value=is_banned, expected_type=type_hints["is_banned"])
            check_type(argname="argument pin_version", value=pin_version, expected_type=type_hints["pin_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "dependencies": dependencies,
            "packages": packages,
        }
        if dependency_types is not None:
            self._values["dependency_types"] = dependency_types
        if is_banned is not None:
            self._values["is_banned"] = is_banned
        if pin_version is not None:
            self._values["pin_version"] = pin_version

    @builtins.property
    def dependencies(self) -> typing.List[builtins.str]:
        '''the names of the dependencies (eg.

        "lodash") which belong to this group
        '''
        result = self._values.get("dependencies")
        assert result is not None, "Required property 'dependencies' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def packages(self) -> typing.List[builtins.str]:
        '''the names of packages in your monorepo which belong to this group, taken from the "name" field in package.json, not the package directory name.'''
        result = self._values.get("packages")
        assert result is not None, "Required property 'packages' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def dependency_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''optionally only apply this group to dependencies of the provided types.'''
        result = self._values.get("dependency_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def is_banned(self) -> typing.Optional[builtins.bool]:
        '''optionally force all dependencies in this group to be removed.'''
        result = self._values.get("is_banned")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pin_version(self) -> typing.Optional[builtins.str]:
        '''optionally force all dependencies in this group to have this version.'''
        result = self._values.get("pin_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VersionGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/nx-monorepo.WorkspaceConfig",
    jsii_struct_bases=[],
    name_mapping={
        "additional_packages": "additionalPackages",
        "disable_no_hoist_bundled": "disableNoHoistBundled",
        "link_local_workspace_bins": "linkLocalWorkspaceBins",
        "no_hoist": "noHoist",
    },
)
class WorkspaceConfig:
    def __init__(
        self,
        *,
        additional_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        disable_no_hoist_bundled: typing.Optional[builtins.bool] = None,
        link_local_workspace_bins: typing.Optional[builtins.bool] = None,
        no_hoist: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Workspace configurations.

        :param additional_packages: List of additional package globs to include in the workspace. All packages which are parented by the monorepo are automatically added to the workspace, but you can use this property to specify any additional paths to packages which may not be managed by projen.
        :param disable_no_hoist_bundled: Disable automatically applying ``noHoist`` logic for all sub-project "bundledDependencies". Default: false
        :param link_local_workspace_bins: Links all local workspace project bins so they can be used for local development. Package bins are only linked when installed from the registry, however it is very useful for monorepo development to also utilize these bin scripts. When enabled, this flag will recursively link all bins from packages.json files to the root node_modules/.bin.
        :param no_hoist: List of package globs to exclude from hoisting in the workspace.

        :see: https://classic.yarnpkg.com/lang/en/docs/workspaces/
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d35c42589a657431675c30384338a08123b6e1b7d408329665166b9090c6360)
            check_type(argname="argument additional_packages", value=additional_packages, expected_type=type_hints["additional_packages"])
            check_type(argname="argument disable_no_hoist_bundled", value=disable_no_hoist_bundled, expected_type=type_hints["disable_no_hoist_bundled"])
            check_type(argname="argument link_local_workspace_bins", value=link_local_workspace_bins, expected_type=type_hints["link_local_workspace_bins"])
            check_type(argname="argument no_hoist", value=no_hoist, expected_type=type_hints["no_hoist"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if additional_packages is not None:
            self._values["additional_packages"] = additional_packages
        if disable_no_hoist_bundled is not None:
            self._values["disable_no_hoist_bundled"] = disable_no_hoist_bundled
        if link_local_workspace_bins is not None:
            self._values["link_local_workspace_bins"] = link_local_workspace_bins
        if no_hoist is not None:
            self._values["no_hoist"] = no_hoist

    @builtins.property
    def additional_packages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of additional package globs to include in the workspace.

        All packages which are parented by the monorepo are automatically added to the workspace, but you can use this
        property to specify any additional paths to packages which may not be managed by projen.
        '''
        result = self._values.get("additional_packages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def disable_no_hoist_bundled(self) -> typing.Optional[builtins.bool]:
        '''Disable automatically applying ``noHoist`` logic for all sub-project "bundledDependencies".

        :default: false
        '''
        result = self._values.get("disable_no_hoist_bundled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def link_local_workspace_bins(self) -> typing.Optional[builtins.bool]:
        '''Links all local workspace project bins so they can be used for local development.

        Package bins are only linked when installed from the registry, however it is very useful
        for monorepo development to also utilize these bin scripts. When enabled, this flag will
        recursively link all bins from packages.json files to the root node_modules/.bin.
        '''
        result = self._values.get("link_local_workspace_bins")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def no_hoist(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of package globs to exclude from hoisting in the workspace.

        :see: https://classic.yarnpkg.com/blog/2018/02/15/nohoist/
        '''
        result = self._values.get("no_hoist")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "MonorepoUpgradeDepsOptions",
    "NxMonorepoProject",
    "NxMonorepoProjectOptions",
    "NxProject",
    "NxWorkspace",
    "SemverGroup",
    "SyncpackConfig",
    "VersionGroup",
    "WorkspaceConfig",
    "nx",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import nx

def _typecheckingstub__4c1e96ba8c2eed7a2799c05d61a028d1e50d166fd4fda4afd2a90eb0eeecca27(
    *,
    syncpack_config: typing.Optional[typing.Union[SyncpackConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    task_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b738e62875428e4cd471aea732c48cddb94f8be4d9c7a17543f94980301f414f(
    dependent: _projen_04054675.Project,
    dependee: typing.Union[builtins.str, _projen_04054675.Project],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__469636d8b7ed326548f3fc664c77053d0ee24f82f5f5da9f9451853745100a99(
    dependent: _projen_java_04054675.JavaProject,
    dependee: _projen_java_04054675.JavaProject,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cde40306266f76eabf18157fb7e689332894a985e0d906a86e5ca1d108712f4c(
    name: builtins.str,
    *,
    target: builtins.str,
    configuration: typing.Optional[builtins.str] = None,
    exclude: typing.Optional[builtins.str] = None,
    ignore_cycles: typing.Optional[builtins.bool] = None,
    no_bail: typing.Optional[builtins.bool] = None,
    output_style: typing.Optional[builtins.str] = None,
    parallel: typing.Optional[jsii.Number] = None,
    projects: typing.Optional[typing.Sequence[builtins.str]] = None,
    runner: typing.Optional[builtins.str] = None,
    skip_cache: typing.Optional[builtins.bool] = None,
    verbose: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cc271f5bd784e939a1bce2dbc71bf305a7412e0a56f89da5585d6a59adc0e1d(
    dependent: _projen_python_04054675.PythonProject,
    dependee: _projen_python_04054675.PythonProject,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__723fb65cfda0224919fa6541c686df09d634e2efdcd517f780356d3eff380d51(
    *package_globs: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b076e3e97e6fa0494e8519239ca96623326e0759561b9c979aaa70fc6a588147(
    *,
    name: builtins.str,
    commit_generated: typing.Optional[builtins.bool] = None,
    git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    outdir: typing.Optional[builtins.str] = None,
    parent: typing.Optional[_projen_04054675.Project] = None,
    projen_command: typing.Optional[builtins.str] = None,
    projenrc_json: typing.Optional[builtins.bool] = None,
    projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    renovatebot: typing.Optional[builtins.bool] = None,
    renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    auto_approve_options: typing.Optional[typing.Union[_projen_github_04054675.AutoApproveOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    auto_merge: typing.Optional[builtins.bool] = None,
    auto_merge_options: typing.Optional[typing.Union[_projen_github_04054675.AutoMergeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    clobber: typing.Optional[builtins.bool] = None,
    dev_container: typing.Optional[builtins.bool] = None,
    github: typing.Optional[builtins.bool] = None,
    github_options: typing.Optional[typing.Union[_projen_github_04054675.GitHubOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    gitpod: typing.Optional[builtins.bool] = None,
    mergify: typing.Optional[builtins.bool] = None,
    mergify_options: typing.Optional[typing.Union[_projen_github_04054675.MergifyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    project_type: typing.Optional[_projen_04054675.ProjectType] = None,
    projen_credentials: typing.Optional[_projen_github_04054675.GithubCredentials] = None,
    projen_token_secret: typing.Optional[builtins.str] = None,
    readme: typing.Optional[typing.Union[_projen_04054675.SampleReadmeProps, typing.Dict[builtins.str, typing.Any]]] = None,
    stale: typing.Optional[builtins.bool] = None,
    stale_options: typing.Optional[typing.Union[_projen_github_04054675.StaleOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    vscode: typing.Optional[builtins.bool] = None,
    allow_library_dependencies: typing.Optional[builtins.bool] = None,
    author_email: typing.Optional[builtins.str] = None,
    author_name: typing.Optional[builtins.str] = None,
    author_organization: typing.Optional[builtins.bool] = None,
    author_url: typing.Optional[builtins.str] = None,
    auto_detect_bin: typing.Optional[builtins.bool] = None,
    bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    bugs_email: typing.Optional[builtins.str] = None,
    bugs_url: typing.Optional[builtins.str] = None,
    bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    code_artifact_options: typing.Optional[typing.Union[_projen_javascript_04054675.CodeArtifactOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    entrypoint: typing.Optional[builtins.str] = None,
    homepage: typing.Optional[builtins.str] = None,
    keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
    license: typing.Optional[builtins.str] = None,
    licensed: typing.Optional[builtins.bool] = None,
    max_node_version: typing.Optional[builtins.str] = None,
    min_node_version: typing.Optional[builtins.str] = None,
    npm_access: typing.Optional[_projen_javascript_04054675.NpmAccess] = None,
    npm_registry: typing.Optional[builtins.str] = None,
    npm_registry_url: typing.Optional[builtins.str] = None,
    npm_token_secret: typing.Optional[builtins.str] = None,
    package_manager: typing.Optional[_projen_javascript_04054675.NodePackageManager] = None,
    package_name: typing.Optional[builtins.str] = None,
    peer_dependency_options: typing.Optional[typing.Union[_projen_javascript_04054675.PeerDependencyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    pnpm_version: typing.Optional[builtins.str] = None,
    repository: typing.Optional[builtins.str] = None,
    repository_directory: typing.Optional[builtins.str] = None,
    scoped_packages_options: typing.Optional[typing.Sequence[typing.Union[_projen_javascript_04054675.ScopedPackagesOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    stability: typing.Optional[builtins.str] = None,
    jsii_release_version: typing.Optional[builtins.str] = None,
    major_version: typing.Optional[jsii.Number] = None,
    min_major_version: typing.Optional[jsii.Number] = None,
    npm_dist_tag: typing.Optional[builtins.str] = None,
    post_build_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
    prerelease: typing.Optional[builtins.str] = None,
    publish_dry_run: typing.Optional[builtins.bool] = None,
    publish_tasks: typing.Optional[builtins.bool] = None,
    release_branches: typing.Optional[typing.Mapping[builtins.str, typing.Union[_projen_release_04054675.BranchOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    release_every_commit: typing.Optional[builtins.bool] = None,
    release_failure_issue: typing.Optional[builtins.bool] = None,
    release_failure_issue_label: typing.Optional[builtins.str] = None,
    release_schedule: typing.Optional[builtins.str] = None,
    release_tag_prefix: typing.Optional[builtins.str] = None,
    release_trigger: typing.Optional[_projen_release_04054675.ReleaseTrigger] = None,
    release_workflow_name: typing.Optional[builtins.str] = None,
    release_workflow_setup_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
    versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    workflow_container_image: typing.Optional[builtins.str] = None,
    workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
    default_release_branch: builtins.str,
    artifacts_directory: typing.Optional[builtins.str] = None,
    auto_approve_upgrades: typing.Optional[builtins.bool] = None,
    build_workflow: typing.Optional[builtins.bool] = None,
    build_workflow_triggers: typing.Optional[typing.Union[_projen_github_workflows_04054675.Triggers, typing.Dict[builtins.str, typing.Any]]] = None,
    bundler_options: typing.Optional[typing.Union[_projen_javascript_04054675.BundlerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    code_cov: typing.Optional[builtins.bool] = None,
    code_cov_token_secret: typing.Optional[builtins.str] = None,
    copyright_owner: typing.Optional[builtins.str] = None,
    copyright_period: typing.Optional[builtins.str] = None,
    dependabot: typing.Optional[builtins.bool] = None,
    dependabot_options: typing.Optional[typing.Union[_projen_github_04054675.DependabotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    deps_upgrade: typing.Optional[builtins.bool] = None,
    deps_upgrade_options: typing.Optional[typing.Union[_projen_javascript_04054675.UpgradeDependenciesOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
    jest: typing.Optional[builtins.bool] = None,
    jest_options: typing.Optional[typing.Union[_projen_javascript_04054675.JestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    mutable_build: typing.Optional[builtins.bool] = None,
    npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
    npmignore_enabled: typing.Optional[builtins.bool] = None,
    npm_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    package: typing.Optional[builtins.bool] = None,
    prettier: typing.Optional[builtins.bool] = None,
    prettier_options: typing.Optional[typing.Union[_projen_javascript_04054675.PrettierOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    projen_dev_dependency: typing.Optional[builtins.bool] = None,
    projenrc_js: typing.Optional[builtins.bool] = None,
    projenrc_js_options: typing.Optional[typing.Union[_projen_javascript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    projen_version: typing.Optional[builtins.str] = None,
    pull_request_template: typing.Optional[builtins.bool] = None,
    pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
    release: typing.Optional[builtins.bool] = None,
    release_to_npm: typing.Optional[builtins.bool] = None,
    release_workflow: typing.Optional[builtins.bool] = None,
    workflow_bootstrap_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
    workflow_git_identity: typing.Optional[typing.Union[_projen_github_04054675.GitIdentity, typing.Dict[builtins.str, typing.Any]]] = None,
    workflow_node_version: typing.Optional[builtins.str] = None,
    disable_tsconfig: typing.Optional[builtins.bool] = None,
    disable_tsconfig_dev: typing.Optional[builtins.bool] = None,
    docgen: typing.Optional[builtins.bool] = None,
    docs_directory: typing.Optional[builtins.str] = None,
    entrypoint_types: typing.Optional[builtins.str] = None,
    eslint: typing.Optional[builtins.bool] = None,
    eslint_options: typing.Optional[typing.Union[_projen_javascript_04054675.EslintOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    libdir: typing.Optional[builtins.str] = None,
    projenrc_ts: typing.Optional[builtins.bool] = None,
    projenrc_ts_options: typing.Optional[typing.Union[_projen_typescript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    sample_code: typing.Optional[builtins.bool] = None,
    srcdir: typing.Optional[builtins.str] = None,
    testdir: typing.Optional[builtins.str] = None,
    tsconfig: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    tsconfig_dev: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    tsconfig_dev_file: typing.Optional[builtins.str] = None,
    typescript_version: typing.Optional[builtins.str] = None,
    monorepo_upgrade_deps: typing.Optional[builtins.bool] = None,
    monorepo_upgrade_deps_options: typing.Optional[typing.Union[MonorepoUpgradeDepsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    workspace_config: typing.Optional[typing.Union[WorkspaceConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f9b6741626fc389be079ffde07106d406606b361d760b9d6f5999b8739c6718(
    project: _projen_04054675.Project,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80dc1deed56597718342c982e8e5c8b9441ff9f326ef7b3a55d7139fe335075e(
    project: _projen_04054675.Project,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a76cd792862733ce23cd71fa357bc8e4765d27391214e2477052d22cdd70cfdc(
    project: _projen_04054675.Project,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7694f119757945af275fa1da6a98d29767ad632e77c40c6659cc3fa52f7f967a(
    inputs: typing.Optional[typing.Sequence[typing.Union[builtins.str, _IInput_844dcc6a]]] = None,
    outputs: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18df3f20897c99ed81405d7cb6bf1319f9a33d702d599b746dba5e9445d58799(
    *dependee: typing.Union[builtins.str, _projen_04054675.Project],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1fc0c6d4ed48fa6b591c2f6eb760d1a105804c8b2977d7c4a1bd7383ad62e91(
    *tags: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4135c80ab345edf257a40519f470c3698ab321d47d413e88d471fddec266f302(
    name: builtins.str,
    inputs: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4e6a22faad472bc3a01a88944455bdc78694211a9a3ab8e3f768277b7fa22f2(
    name: builtins.str,
    target: _IProjectTarget_963c071e,
    include_defaults: typing.Optional[typing.Union[builtins.str, builtins.bool]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2c6413f97fd812c8d2c8c962df57749ff79c358f69af1d71f4bb6627a447e37(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d01a4a451fc5f546fd1873c4ba364ee7d223dcf21e9266eba6f234211d36f59(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0979a49c05bce24f7c99794ecd4f290be7cce1322a60a051955879f975f320d5(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__351c7334d1c7664fa8507a5bad91a7f4439f997a77d08c51539a48105f86163f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cae678f0f69ee19577586deaa478e15f1288bbca4f599787c8f71aec317be950(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8386594efa8f970e49738559198399eea321b2a199064942362bb1564030f7e(
    project: _projen_04054675.Project,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__695644f0eecd1924376627c1424be5f5a140237381933295f1e80f7a07f145a9(
    scope: _projen_04054675.Project,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__802546f32bcb961dc69a40dec5fc86f113597e7a893d1f2a6a3937fd36c5c982(
    name: builtins.str,
    inputs: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15b0bbfb5d798c8113892ba448ed658f91d8ffa282270fafee136f9a84b94fa8(
    name: builtins.str,
    target: _IProjectTarget_963c071e,
    merge: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3395df127f6804ff001c56fd57148403ff9293019d38cfdbbacf8a93964efb65(
    read_only_access_token: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1abb24d49fe05a58d9f5daed9e2ce6ac2e746bbfc7bdbc00aa0c71f94f21958(
    value: _INxAffectedConfig_f6105638,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64c689a104fb9ab2e1616db76edf6882af8d61e9ed6fcaff155d15aaf50c652c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b54df1d7b0ed7e22d17c869119f1ef6fafe6e360e2cd0ead989d8659553f301a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ee103672ffd4c42450f81e2b90a8a181a17ab55e52bff2e270a3bc944389a4a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a893b1a3babbb835b1a6cda09d9bd1e1c5907924715be1770d1289e25d99946(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a37d2f6ad8dbec05d4efad5e60e6c7ea9150a5b177d62493477b0fc78b12cca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06d365fd7564cdcc6b94e99732313d1713798c21094146651be691e459863f71(
    value: typing.Mapping[builtins.str, typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__119f31ba008edd00434e5b3f549fb6a094866bd2470957d2d227d69a8cc8ce8b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__358d9f024d09e37b4537491c2dcf8f7a13c0f036968bde12f7b91c6119e96b09(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9097f9c3bcd4b178a1ca6b32ca26843cea639c347870a0fb6e8cbd48f49e5823(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ce38c34ab569ebd21cb5108a33114f99224a7285f5054bfad9938a82c9b840b(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af4651413cd46bdb50c4e4b9c13afa04f3a15bf16da8d963fc6a6b364e19aa4d(
    value: typing.Mapping[builtins.str, _IProjectTarget_963c071e],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a6d1c0b12954870f9022d8b0eb06bbb24e16d62a2cdfc0ca41630f3ae2e3352(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa4ffd9f7ecea4596de010cb12bb45325114e74f5bb90543d1b5556fd723a59f(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af52b1df34ba2dfccaa7543a6a4a262e81ddbe95c35b8f17c283f21c9a361bc1(
    value: typing.Optional[_IWorkspaceLayout_91f3d180],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c17c85363fc4b46a5bdccfd298a080815f6cec752f651ba4183f84a542d398b3(
    *,
    dependencies: typing.Sequence[builtins.str],
    packages: typing.Sequence[builtins.str],
    range: builtins.str,
    dependency_types: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb223affa13a00894ad326c57270f418883297270633ef343c4dfdb409de6995(
    *,
    dependency_types: typing.Sequence[builtins.str],
    dev: builtins.bool,
    filter: builtins.str,
    indent: builtins.str,
    overrides: builtins.bool,
    peer: builtins.bool,
    pnpm_overrides: builtins.bool,
    prod: builtins.bool,
    resolutions: builtins.bool,
    semver_groups: typing.Sequence[typing.Union[SemverGroup, typing.Dict[builtins.str, typing.Any]]],
    semver_range: builtins.str,
    sort_az: typing.Sequence[builtins.str],
    sort_first: typing.Sequence[builtins.str],
    source: typing.Sequence[builtins.str],
    version_groups: typing.Sequence[typing.Union[VersionGroup, typing.Dict[builtins.str, typing.Any]]],
    workspace: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d36097d2d6d9a3f5db57da121c324aa1a4c90571bf11d93a2e34f0a5b3f28966(
    *,
    dependencies: typing.Sequence[builtins.str],
    packages: typing.Sequence[builtins.str],
    dependency_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    is_banned: typing.Optional[builtins.bool] = None,
    pin_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d35c42589a657431675c30384338a08123b6e1b7d408329665166b9090c6360(
    *,
    additional_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
    disable_no_hoist_bundled: typing.Optional[builtins.bool] = None,
    link_local_workspace_bins: typing.Optional[builtins.bool] = None,
    no_hoist: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
