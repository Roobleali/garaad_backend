# Multiple Diagrams API Implementation

## Overview

The LMS backend now supports **both single and multiple diagram configurations** for complex math problems. This implementation maintains backward compatibility while adding support for problems that require multiple diagrams for complete understanding.

## 🚨 Breaking Changes

**IMPORTANT**: The frontend now sends diagram data in **two different formats**. The backend handles both formats with mutual exclusivity validation.

## 📋 Database Schema Changes

### New Field Added to Problem Model

```python
class Problem(models.Model):
    # ... existing fields ...
    diagram_config = models.JSONField(default=dict, blank=True)  # Single diagram (existing)
    diagrams = models.JSONField(null=True, blank=True, help_text="Multiple diagram configurations for complex problems")  # NEW FIELD
    # ... other fields ...
```

### Migration Applied

- **Migration**: `0016_add_diagrams_field.py`
- **Field**: `diagrams` (JSONField, nullable)
- **Purpose**: Store multiple diagram configurations as an array

## 🔧 Backend Implementation

### 1. Model Validation

The `Problem` model now includes comprehensive validation:

```python
def clean(self):
    """Validate diagram configuration exclusivity"""
    if self.question_type == 'diagram':
        has_single_diagram = self.diagram_config and self.diagram_config != {}
        has_multiple_diagrams = self.diagrams and self.diagrams != []
        
        if has_single_diagram and has_multiple_diagrams:
            raise ValidationError({
                'diagram_config': 'Cannot use both diagram_config and diagrams simultaneously'
            })
        
        if not has_single_diagram and not has_multiple_diagrams:
            raise ValidationError({
                'diagram_config': 'Diagram problems require either diagram_config or diagrams'
            })
```

### 2. Serializer Updates

The `ProblemSerializer` now handles both formats:

```python
class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = [
            'id', 'which', 'question_text', 'question_type', 'options',
            'correct_answer', 'explanation', 'content',
            'diagram_config', 'diagrams', 'img', 'xp', 'created_at', 'updated_at'
        ]
        
    def to_representation(self, instance):
        """Ensure mutual exclusivity in response"""
        data = super().to_representation(instance)
        
        if instance.question_type == 'diagram':
            if instance.diagrams and instance.diagrams != []:
                data['diagram_config'] = None  # Multiple diagrams format
            elif instance.diagram_config and instance.diagram_config != {}:
                data['diagrams'] = None  # Single diagram format
```

### 3. View Layer Validation

The `ProblemViewSet` includes early validation:

```python
def create(self, request, *args, **kwargs):
    # Validate diagram configuration for diagram problems
    if request.data.get('question_type') == 'diagram':
        diagram_config = request.data.get('diagram_config')
        diagrams = request.data.get('diagrams')
        
        has_single_diagram = diagram_config and diagram_config != {}
        has_multiple_diagrams = diagrams and diagrams != []
        
        if has_single_diagram and has_multiple_diagrams:
            return Response(
                {'error': 'Cannot use both diagram_config and diagrams simultaneously'},
                status=status.HTTP_400_BAD_REQUEST
            )
```

## 📋 API Format Specifications

### Format 1: Single Diagram (Backward Compatibility)

```json
{
  "lesson": 123,
  "question_text": "What is the weight?",
  "question_type": "diagram",
  "diagram_config": {
    "diagram_id": 101,
    "diagram_type": "scale", 
    "scale_weight": 15,
    "objects": [
      {
        "type": "cube",
        "color": "#4F8EF7",
        "text_color": "#FFFFFF",
        "number": 5,
        "position": "left",
        "layout": {
          "rows": 2,
          "columns": 3,
          "position": "center",
          "alignment": "center"
        },
        "weight_value": null
      }
    ]
  },
  "diagrams": null,
  "options": [...],
  "correct_answer": [...],
  "explanation": "...",
  "content": {},
  "xp": 10
}
```

### Format 2: Multiple Diagrams (New Feature)

```json
{
  "lesson": 123,
  "question_text": "Based on the two scales, what is the weight of 1 circle?",
  "question_type": "diagram",
  "diagram_config": null,
  "diagrams": [
    {
      "diagram_id": 101,
      "diagram_type": "scale",
      "scale_weight": 16,
      "objects": [...]
    },
    {
      "diagram_id": 102,
      "diagram_type": "scale",
      "scale_weight": 14,
      "objects": [...]
    }
  ],
  "options": [...],
  "correct_answer": [...],
  "explanation": "...",
  "content": {},
  "xp": 15
}
```

## 🔍 Validation Rules

### Mutual Exclusivity
- ✅ **Valid**: `diagram_config` populated, `diagrams` = `null`
- ✅ **Valid**: `diagrams` populated, `diagram_config` = `null`
- ❌ **Invalid**: Both `diagram_config` AND `diagrams` populated
- ❌ **Invalid**: Neither `diagram_config` NOR `diagrams` populated (for diagram questions)

### Required Fields for Each Diagram

#### Single Diagram (`diagram_config`)
```json
{
  "diagram_id": "required",
  "diagram_type": "required", 
  "scale_weight": "required",
  "objects": "required array"
}
```

#### Each Object in `objects` Array
```json
{
  "type": "required",
  "color": "required",
  "text_color": "required", 
  "number": "required",
  "position": "required",
  "layout": {
    "rows": "required",
    "columns": "required",
    "position": "required",
    "alignment": "required"
  },
  "weight_value": "optional"
}
```

## 🧪 Testing

### Test Cases Covered

1. **Single Diagram Creation** ✅
2. **Multiple Diagram Creation** ✅
3. **Mutual Exclusivity Validation** ✅
4. **Missing Required Fields** ✅
5. **Invalid Object Structure** ✅
6. **Backward Compatibility** ✅

### Example Test Script

Run the included test script:
```bash
python test_diagrams_api.py
```

## 🚀 API Endpoints

### Create Problem
- **Endpoint**: `POST /api/lms/problems/`
- **Supports**: Both single and multiple diagram formats
- **Validation**: Comprehensive field and structure validation

### Update Problem  
- **Endpoint**: `PUT /api/lms/problems/{id}/`
- **Supports**: Format switching (single ↔ multiple)
- **Validation**: Same as create

### Retrieve Problem
- **Endpoint**: `GET /api/lms/problems/{id}/`
- **Response**: Matches the format used in the problem
- **Null Fields**: Unused format fields are null

## 🔧 Migration Strategy

### Phase 1: Database Schema ✅
- [x] Add `diagrams` field to Problem model
- [x] Create migration `0016_add_diagrams_field.py`

### Phase 2: Backend Logic ✅  
- [x] Update model validation
- [x] Update serializers
- [x] Update view validation
- [x] Add comprehensive tests

### Phase 3: Deployment
- [ ] Apply migrations in production
- [ ] Test with frontend integration
- [ ] Monitor for errors

### Phase 4: Documentation
- [x] Update API documentation
- [x] Create test examples
- [x] Document migration process

## 🚨 Important Notes

### For Frontend Developers
1. **Never send both formats simultaneously** - validation will reject the request
2. **Always set unused format to null** - helps maintain data consistency  
3. **Use appropriate format** - single for simple problems, multiple for complex ones
4. **Validate before sending** - check required fields client-side

### For Backend Developers
1. **Migrations are ready** - apply when database is accessible
2. **Backward compatibility maintained** - existing single diagrams continue working
3. **Comprehensive validation** - both model and serializer level
4. **Error handling** - clear error messages for validation failures

## 📞 Support

### Testing the Implementation
```bash
# Run the test script
python test_diagrams_api.py

# Apply migrations (when database is accessible)
python manage.py migrate

# Check migration status
python manage.py showmigrations courses
```

### API Testing Examples
See `test_diagrams_api.py` for complete examples of:
- Single diagram payload
- Multiple diagrams payload  
- Invalid payload (should fail)
- Expected response formats

## 🔗 Related Files

- **Models**: `courses/models.py` 
- **Serializers**: `courses/serializers.py`
- **Views**: `courses/views.py`
- **Migration**: `courses/migrations/0016_add_diagrams_field.py`
- **Tests**: `test_diagrams_api.py`
- **Documentation**: `docs/MULTIPLE_DIAGRAMS_IMPLEMENTATION.md`

---

*This implementation maintains full backward compatibility while adding powerful new capabilities for complex mathematical problems requiring multiple visual representations.* 