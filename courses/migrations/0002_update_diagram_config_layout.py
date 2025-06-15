from django.db import migrations

def update_diagram_config_layout(apps, schema_editor):
    Problem = apps.get_model('courses', 'Problem')
    for problem in Problem.objects.filter(question_type='diagram'):
        if problem.diagram_config:
            # Handle both single object and array of objects
            if isinstance(problem.diagram_config, dict):
                objects = problem.diagram_config.get('objects', [])
            else:
                objects = []
                for config in problem.diagram_config:
                    objects.extend(config.get('objects', []))
            
            # Update each object's layout
            for obj in objects:
                if 'orientation' in obj:
                    orientation = obj.pop('orientation')
                    # Convert orientation to layout
                    layout = {
                        "rows": 1,
                        "columns": 1,
                        "position": obj.get('position', 'center'),
                        "alignment": "center"
                    }
                    
                    # Adjust rows and columns based on orientation
                    if orientation == 'vertical':
                        layout['rows'] = obj.get('number', 1)
                        layout['columns'] = 1
                    elif orientation == 'horizontal':
                        layout['rows'] = 1
                        layout['columns'] = obj.get('number', 1)
                    
                    obj['layout'] = layout
            
            problem.save()

def reverse_diagram_config_layout(apps, schema_editor):
    Problem = apps.get_model('courses', 'Problem')
    for problem in Problem.objects.filter(question_type='diagram'):
        if problem.diagram_config:
            # Handle both single object and array of objects
            if isinstance(problem.diagram_config, dict):
                objects = problem.diagram_config.get('objects', [])
            else:
                objects = []
                for config in problem.diagram_config:
                    objects.extend(config.get('objects', []))
            
            # Revert each object's layout back to orientation
            for obj in objects:
                if 'layout' in obj:
                    layout = obj.pop('layout')
                    # Convert layout back to orientation
                    if layout['rows'] > layout['columns']:
                        obj['orientation'] = 'vertical'
                    elif layout['columns'] > layout['rows']:
                        obj['orientation'] = 'horizontal'
                    else:
                        obj['orientation'] = 'none'
                    
                    # Keep the position if it exists
                    if 'position' in layout:
                        obj['position'] = layout['position']
            
            problem.save()

class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            update_diagram_config_layout,
            reverse_diagram_config_layout
        ),
    ] 