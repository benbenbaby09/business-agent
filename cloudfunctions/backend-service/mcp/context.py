import uuid
from datetime import datetime

class Resource:
    def __init__(self, uri, name, description, mime_type, content):
        self.uri = uri
        self.name = name
        self.description = description
        self.mime_type = mime_type
        self.content = content

class Tool:
    def __init__(self, name, description, parameters):
        self.name = name
        self.description = description
        self.parameters = parameters

class Prompt:
    def __init__(self, name, description, template, arguments):
        self.name = name
        self.description = description
        self.template = template
        self.arguments = arguments

class Context:
    def __init__(self, id, tenant_id, name, metadata=None):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.metadata = metadata or {}
        self.resources = []
        self.tools = []
        self.prompts = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def add_resource(self, resource):
        """添加资源"""
        self.resources.append(resource)
        self.updated_at = datetime.now()

    def add_tool(self, tool):
        """添加工具"""
        self.tools.append(tool)
        self.updated_at = datetime.now()

    def add_prompt(self, prompt):
        """添加提示词"""
        self.prompts.append(prompt)
        self.updated_at = datetime.now()

    def get_resource(self, uri):
        """获取资源"""
        for resource in self.resources:
            if resource.uri == uri:
                return resource
        return None

    def get_tool(self, name):
        """获取工具"""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    def get_prompt(self, name):
        """获取提示词"""
        for prompt in self.prompts:
            if prompt.name == name:
                return prompt
        return None

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'metadata': self.metadata,
            'resources': [{
                'uri': r.uri,
                'name': r.name,
                'description': r.description,
                'mime_type': r.mime_type,
                'content': r.content
            } for r in self.resources],
            'tools': [{
                'name': t.name,
                'description': t.description,
                'parameters': t.parameters
            } for t in self.tools],
            'prompts': [{
                'name': p.name,
                'description': p.description,
                'template': p.template,
                'arguments': p.arguments
            } for p in self.prompts],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
