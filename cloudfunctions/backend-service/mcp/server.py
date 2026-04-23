import uuid
from .context import Context, Resource, Tool, Prompt

class MCPServer:
    def __init__(self):
        self.contexts = {}

    def init_app(self, app):
        """初始化应用"""
        self.app = app
        # 可以在这里添加应用级别的配置

    def create_context(self, tenant_id, metadata=None):
        """创建上下文"""
        context_id = str(uuid.uuid4())
        context = Context(
            id=context_id,
            tenant_id=tenant_id,
            name=metadata.get('name', 'Default Context'),
            metadata=metadata
        )
        self.contexts[context_id] = context
        return context_id

    def get_context(self, context_id):
        """获取上下文"""
        return self.contexts.get(context_id)

    def list_contexts(self, tenant_id):
        """列出上下文"""
        return [ctx for ctx in self.contexts.values() if ctx.tenant_id == tenant_id]

    def delete_context(self, context_id):
        """删除上下文"""
        if context_id in self.contexts:
            del self.contexts[context_id]
            return True
        return False

    def add_resource(self, context_id, resource_data):
        """添加资源"""
        context = self.get_context(context_id)
        if not context:
            return None

        resource = Resource(
            uri=resource_data.get('uri'),
            name=resource_data.get('name'),
            description=resource_data.get('description'),
            mime_type=resource_data.get('mime_type'),
            content=resource_data.get('content')
        )
        context.add_resource(resource)
        return resource

    def add_tool(self, context_id, tool_data):
        """添加工具"""
        context = self.get_context(context_id)
        if not context:
            return None

        tool = Tool(
            name=tool_data.get('name'),
            description=tool_data.get('description'),
            parameters=tool_data.get('parameters', {})
        )
        context.add_tool(tool)
        return tool

    def add_prompt(self, context_id, prompt_data):
        """添加提示词"""
        context = self.get_context(context_id)
        if not context:
            return None

        prompt = Prompt(
            name=prompt_data.get('name'),
            description=prompt_data.get('description'),
            template=prompt_data.get('template'),
            arguments=prompt_data.get('arguments', [])
        )
        context.add_prompt(prompt)
        return prompt

    def get_resource(self, context_id, uri):
        """获取资源"""
        context = self.get_context(context_id)
        if not context:
            return None
        return context.get_resource(uri)

    def get_tool(self, context_id, name):
        """获取工具"""
        context = self.get_context(context_id)
        if not context:
            return None
        return context.get_tool(name)

    def get_prompt(self, context_id, name):
        """获取提示词"""
        context = self.get_context(context_id)
        if not context:
            return None
        return context.get_prompt(name)

    def render_prompt(self, context_id, name, arguments):
        """渲染提示词"""
        prompt = self.get_prompt(context_id, name)
        if not prompt:
            return None

        rendered = prompt.template
        for arg in prompt.arguments:
            arg_name = arg.get('name')
            if arg_name in arguments:
                rendered = rendered.replace(f'{{{arg_name}}}', str(arguments[arg_name]))

        return rendered

# 创建MCP服务器实例
mcp_server = MCPServer()
