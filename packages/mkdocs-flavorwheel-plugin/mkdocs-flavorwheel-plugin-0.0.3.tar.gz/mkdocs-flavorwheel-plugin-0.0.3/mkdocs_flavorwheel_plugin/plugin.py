import os
import sys
from timeit import default_timer as timer
from datetime import datetime, timedelta

from mkdocs import utils as mkdocs_utils
from mkdocs.config import config_options, Config
from mkdocs.plugins import BasePlugin


class FlavorWheelPlugin(BasePlugin):
    config_scheme = (
        ('param', config_options.Type(str, default='')),
    )

    def __init__(self):
        self.enabled = True
        self.total_time = 0

    def on_serve(self, server, **kwargs):
        return server

    def on_pre_build(self, config, **kwargs):
        return

    def on_files(self, files, config, **kwargs):
        return files

    def on_nav(self, nav, config, files, **kwargs):
        return nav

    def on_env(self, env, config, files, **kwargs):
        return env

    def on_config(self, config, **kwargs):
        return config

    def on_post_build(self, config, **kwargs):
        return

    def on_pre_template(self, template, template_name, config):
        return template

    def on_template_context(self, context, template_name, config):
        return context

    def on_post_template(self, output_content, template_name, config):
        return output_content

    def on_pre_page(self, page, config, files, **kwargs):
        return page

    def on_page_read_source(self, page, config, **kwargs):
        return ""

    def on_page_markdown(self, markdown, page, config, **kwargs):
        if 'flavorwheel' in page.meta:
            self.flavorwheel = page.meta['flavorwheel']
        else:
            self.flavorwheel = None
        return markdown

    def on_page_content(self, html, page, config, **kwargs):
        if self.flavorwheel:
            flavorwheel_html = f'<div class="flavorwheel">{self.flavorwheel}</div>'
            html = html.replace('</h1>', f'</h1>{flavorwheel_html}')
        return html

    def on_page_context(self, context, page, config, nav, **kwargs):
        return context

    def on_post_page(self, output_content, page, config, **kwargs):
        return output_content