import markdown
import re
from jinja2 import Environment, PackageLoader


class Section(object):
    def __init__(self, id='', name='', methods=None):
        self.id = id
        self.name = name
        self.methods = []

        for help_content, example_content in methods or []:
            if example_content is '':
                parts = help_content.split('{example}')
                if len(parts) % 2 == 1:
                    parts.append('')

                for i in xrange(0, len(parts), 2):
                    h = parts[i]
                    e = parts[i+1]

                    # replace language content
                    e = re.sub('```(?P<lang>[\w-]+)', '<pre><code class="\g<lang>">', e)
                    e = re.sub('```', '\n</code></pre>', e)

                    e = markdown.markdown(e)

                    e = re.sub('<pre><code>', '<pre><code class="python">', e)
                    e = re.sub('<pre>(?!<code[^>]*>)', '<pre><code class="python">', e)
                    e = re.sub('(?!</code>)</pre>', '</code></pre>', e)

                    self.methods.append((
                        len(self.methods),
                        markdown.markdown(h),
                        e
                    ))
            else:
                # replace language content
                example_content = re.sub('```(?P<lang>[\w-]+)', '<pre><code class="\g<lang>">', example_content)
                example_content = re.sub('```', '\n</code></pre>', example_content)

                example_content = markdown.markdown(example_content)

                example_content = re.sub('<pre>(?!<code>)', '<pre><code class="python">', example_content)
                example_content = re.sub('(?!</code>)</pre>', '</code></pre>', example_content)

                self.methods.append((
                    len(self.methods),
                    markdown.markdown(help_content),
                    example_content
                ))


class SectionGroup(object):
    def __init__(self, name='', sections=None):
        self.name = name
        self.sections = sections or []


class Documentation(object):
    def __init__(self, package, folder, template):
        self.__environment = Environment(loader=PackageLoader(package, folder))

    def options(self, api, request):
        opts = {
            'application': api.application,
            'url': request.route_url(api.route_name, traverse='').rstrip('/')
        }
        return opts

    def introduction(self, api, request):
        options = self.options(api, request)

        help_template = self.__environment.get_template('introduction.md.jinja')
        help_content = help_template.render(**options)

        #example_template = self.__environment.get_template('intro_example.md.jinja')
        #example_content = example_template.render(**options)

        section = Section(
            id='introduction',
            name='Introduction',
            methods=[(help_content, '')]
        )
        return section


    def render(self, api, request):
        template = self.__environment.get_template('documentation.html.jinja')
        options = self.options(api, request)
        options['section_groups'] = api.section_groups(request)
        return template.render(**options)