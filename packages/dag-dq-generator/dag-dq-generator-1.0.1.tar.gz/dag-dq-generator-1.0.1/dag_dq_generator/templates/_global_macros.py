# Creates a group with:
#
#
#
{% macro create_group(pipeline_settings, tasks_groups_str, group, indent_width) %}
{% filter indent(width=indent_width) %}
with TaskGroup(group_id="{{group.group_name}}") as {{group.group_name}}:

    tasks = [] # list of tasks in group
    {% for task in group.tasks%}
    {{task.task_id}}_args = {{task.arguments|default([])}}

    {% if task.operator == 'DatabricksSqlOperator' %} # Generate SQLOperator task
    {% if pipeline_settings.pull_fiscal_attributes -%}
    {{task.task_id}}_args['sql'] = {{task.task_id}}_args['sql'] if isinstance({{task.task_id}}_args['sql'], list) else [{{task.task_id}}_args['sql']]
    for k,v in {'${' + k + '}': v for k,v in fiscal_parameters.items()}.items(): {{task.task_id}}_args['sql'] = [sql.replace(k, v) for sql in {{task.task_id}}_args['sql']]
    {%- endif %}

    {{task.task_id}} = DatabricksSqlOperator(
        task_id='{{task.task_id}}',
        on_success_callback=_task_on_success_callback,
        **{{task.task_id}}_args
    )
    
    {% elif task.operator == 'DatabricksRunNowOperator' %} # Generate RunNowOperator task
    {% if pipeline_settings.pull_fiscal_attributes -%}
    {{task.task_id}}_args['notebook_params'] = {**{{task.task_id}}_args.get('notebook_params', {}), **fiscal_parameters}
    {% if 'python_params' in task.arguments -%} {{task.task_id}}_args['python_params'] = {**{{task.task_id}}_args.get('python_params', {}), **fiscal_parameters} {%- endif %}
    {% if 'jar_params' in task.arguments -%} {{task.task_id}}_args['jar_params'] = {**{{task.task_id}}_args.get('jar_params', {}), **fiscal_parameters} {%- endif %}
    {% if 'spark_submit_params' in task.arguments -%} {{task.task_id}}_args['spark_submit_params'] = {**{{task.task_id}}_args.get('spark_submit_params', {}), **fiscal_parameters} {%- endif %}
    {%- endif %}

    {{task.task_id}} = DatabricksRunNowOperator(
        task_id='{{task.task_id}}',
        on_success_callback=_task_on_success_callback,
        **{{task.task_id}}_args
    )

    {% elif task.operator == 'DatabricksSubmitRunOperator' %} # Generate SubmitNowOperator task
    {% if pipeline_settings.pull_fiscal_attributes -%}
    {% if 'notebook_task' in task.arguments -%}
    for k,v in {'${' + k + '}': v for k,v in fiscal_parameters.items()}.items(): 
        for bk, bv in {{task.task_id}}_args['notebook_task'].get('base_parameters', {}).items(): {{task.task_id}}_args['notebook_task'].get('base_parameters', {})[bk] = bv.replace(k, v)
    {{task.task_id}}_args['notebook_task'] = {**{{task.task_id}}_args['notebook_task'], **{'base_parameters': {**{{task.task_id}}_args['notebook_task'].get('base_parameters', {}), **fiscal_parameters}}} if 'notebook_task' in {{task.task_id}}_args else {'base_parameters': fiscal_parameters} {%- endif %}
    {% if 'spark_python_task' in task.arguments -%} {{task.task_id}}_args['spark_python_task'] = {**{{task.task_id}}_args['spark_python_task'], **{'base_parameters': {**{{task.task_id}}_args['spark_python_task'].get('base_parameters', {}), **fiscal_parameters}}} if 'spark_python_task' in {{task.task_id}}_args else {'base_parameters': fiscal_parameters} {%- endif %}
    {% if 'spark_jar_task' in task.arguments -%} {{task.task_id}}_args['spark_jar_task'] = {**{{task.task_id}}_args['spark_jar_task'], **{'base_parameters': {**{{task.task_id}}_args['spark_jar_task'].get('base_parameters', {}), **fiscal_parameters}}} if 'spark_jar_task' in {{task.task_id}}_args else {'base_parameters': fiscal_parameters} {%- endif %}
    {% if 'spark_submit_task' in task.arguments -%} {{task.task_id}}_args['spark_submit_task'] = {**{{task.task_id}}_args['spark_submit_task'], **{'base_parameters': {**{{task.task_id}}_args['spark_submit_task'].get('base_parameters', {}), **fiscal_parameters}}} if 'spark_submit_task' in {{task.task_id}}_args else {'base_parameters': fiscal_parameters} {%- endif %}
    {%- endif %}

    {{task.task_id}} = DatabricksSubmitRunOperator(
        task_id='{{task.task_id}}',
        new_cluster={{task.new_cluster}},
        on_success_callback=_task_on_success_callback,
        **{{task.task_id}}_args
    )

    {% elif task.operator == 'TriggerDagRunOperator' %} # Generate TriggerDagRunOperator task

    {{task.task_id}} = TriggerDagRunOperator(
        task_id='{{task.task_id}}',
        on_success_callback=_task_on_success_callback,
        **{{task.task_id}}_args
    )

    {% elif task.operator == 'DateTimeSensor' %} # Generate DateTimeSensor task
    
    {{task.task_id}}_args['target_time'] = eval({{task.task_id}}_args['target_time'])

    {{task.task_id}} = DateTimeSensor(
        task_id='{{task.task_id}}',
        on_success_callback=_task_on_success_callback,
        **{{task.task_id}}_args
    )

    {% elif task.operator == 'SubGroupOperator' %} # Generate SubGroup
    {% set _ = task.update({'group_name': task.task_id}) %}
    {{create_group(pipeline_settings, tasks_groups_str + '.' + group.group_name, task, 4)}}

    {% else %}
    {% set msg = "Unsupported operator '" + task.operator + "' found in configuration file. Supported operators are [DatabricksSqlOperator, DatabricksRunNowOperator, DatabricksSubmitRunOperator, TriggerDagRunOperator, DateTimeSensor, SubGroupOperator]"%}}
        {{ raise(msg) }}

    {% endif %}

    {% if task.enable_check -%}
    
    _task_id = {{task.task_id}}

    with TaskGroup(group_id="{{task.task_id}}_chk") as {{task.task_id}}:
        
        {{task.task_id}}_args = {{task.check_arguments}}

        {% if pipeline_settings.pull_fiscal_attributes -%}
        {{task.task_id}}_args['sql'] = {{task.task_id}}_args['sql'] if isinstance({{task.task_id}}_args['sql'], list) else [{{task.task_id}}_args['sql']]
        for k,v in {'${' + k + '}': v for k,v in fiscal_parameters.items()}.items(): {{task.task_id}}_args['sql'] = [sql.replace(k, v) for sql in {{task.task_id}}_args['sql']]
        {%- endif %}
        
        {{task.task_id}}_qry = DatabricksSqlOperator(
            task_id='{{task.task_id}}_check',
            on_success_callback=_task_on_success_callback,
            **{{task.task_id}}_args
        )
        
        {{task.task_id}}_check = ShortCircuitOperator(
            task_id='{{task.task_id}}_check_chk',
            op_kwargs={'sql_task_id': '{{tasks_groups_str}}.{{group.group_name}}.{{task.task_id}}.{{task.task_id}}_check', 'sql_task_args': {{task.task_id}}_args},
            ignore_downstream_trigger_rules=False,
            python_callable=_verify_check_response,
        )

        {{task.task_id}}_run = _task_id

        {{task.task_id}}_qry >> {{task.task_id}}_check >> {{task.task_id}}_run

    {%- endif %}
    
    tasks.append({{task.task_id}})

    {% endfor %}

    {% if group.is_sequential_execution -%}
    # Set sequential execution for {{group.group_name}} elements
    chain(*tasks)
    {% endif %}
{% if tasks_groups_str == 'Execs' %}
exec_tasks_groups.append({{group.group_name}})
{% endif %}
{% endfilter %}
{% endmacro %}