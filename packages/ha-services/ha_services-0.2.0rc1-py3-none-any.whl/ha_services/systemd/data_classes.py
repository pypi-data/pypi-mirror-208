import dataclasses
from pathlib import Path
from string import Template

from bx_py_utils.path import assert_is_dir, assert_is_file

from ha_services.cli_tools.richt_utils import human_error
from ha_services.mqtt4homeassistant.utilities.string_utils import slugify
from ha_services.systemd.defaults import (
    get_demo_exec_start,
    get_template_path,
    get_user_group,
    get_user_name,
    get_work_directory,
)
from ha_services.systemd.template import InvalidTemplate, validate_template


@dataclasses.dataclass
class BaseSystemdServiceTemplateContext:
    """
    Context values for the systemd service file content
    """

    verbose_service_name: str  # Must be set in child class!

    user: str = dataclasses.field(default_factory=get_user_name)
    group: str = dataclasses.field(default_factory=get_user_group)
    work_dir: Path = dataclasses.field(default_factory=get_work_directory)

    exec_start: str = dataclasses.field(default_factory=get_demo_exec_start)

    # Optional values, will be automatically filled:
    syslog_identifier: str = None


@dataclasses.dataclass
class BaseSystemdServiceInfo:
    """
    Information for systemd helper functions
    """

    template_context: BaseSystemdServiceTemplateContext  # Must be set in child class!

    template_path: Path = dataclasses.field(default_factory=get_template_path)

    systemd_base_path: Path = Path('/etc/systemd/system/')

    # Set by post init from "template_context" information:
    service_slug: str = None
    service_file_path: Path = None

    def __post_init__(self):
        assert_is_dir(self.systemd_base_path)
        assert_is_dir(self.template_context.work_dir)
        assert_is_file(self.template_path)

        if not self.service_slug:
            self.service_slug = slugify(self.template_context.verbose_service_name, sep='_').lower()

        if not self.template_context.syslog_identifier:
            self.template_context.syslog_identifier = self.service_slug

        self.service_file_path = self.systemd_base_path / f'{self.service_slug}.service'

        try:
            validate_template(content=self.get_template_content(), context=self.get_template_context())
        except InvalidTemplate as err:
            human_error(
                f'Template {self.template_path} is not valid:\n{err}',
                title='[red]invalid Systemd template',
                exception=err,
            )

    def get_template_content(self) -> str:
        """
        Returns the content of template to generate the systemd service file
        """
        return self.template_path.read_text(encoding='UTF-8').strip()

    def get_template_context(self) -> dict:
        """
        Returns the context  for the systems service file template
        """
        context = dataclasses.asdict(self.template_context)
        return context

    def get_compiled_service(self) -> str:
        """
        Returns the completed systems service file content
        """
        template = self.get_template_content()
        template = Template(template)
        context = self.get_template_context()
        content = template.substitute(**context)
        return content
