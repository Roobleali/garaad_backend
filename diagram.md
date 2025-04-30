
Example Problem in backend: 

[
    {
        "id": 7,
        "question_text": "Waxa miisaanka ku yaal ayaa muujinaya culayska alaabta. Immisa ayuu le'eg yahay hal laba jibbaaran?",
        "question_type": "diagram",
        "options": [
            {
                "id": "a",
                "text": "4"
            },
            {
                "id": "b",
                "text": "8"
            },
            {
                "id": "c",
                "text": "10"
            },
            {
                "id": "d",
                "text": "16"
            }
        ],
        "correct_answer": [
            {
                "id": "c",
                "text": "10"
            }
        ],
        "explanation": "Since there are 4 squares weighing 40, each square weighs 40 / 4 = 10.",
        "content": [
            {}
        ],
        "diagram_config": [
            {
                "objects": [
                    {
                        "type": "cube",
                        "color": "blue",
                        "number": 3,
                        "position": "center",
                        "orientation": "vertical"
                    },
                    {
                        "type": "triangle",
                        "color": "gray",
                        "number": 1,
                        "position": "center",
                        "orientation": "none",
                        "weight_value": 10
                    }
                ],
                "diagram_id": 1,
                "diagram_type": "scale",
                "scale_weight": 25
            }
        ],
        "created_at": "2025-04-21T09:13:55.103330Z",
        "updated_at": "2025-04-29T13:50:41.216425Z"
    }
]



 Front-End Script

1. **Fetch the Data**  
   - Get the JSON from the backend (e.g., via an API).  
   - Parse it into a usable format (an array of diagrams).

2. **Prepare the Display**  
   - Create a container on the webpage to hold all diagrams.  
   - Clear any existing content in the container.

3. **Loop Through Diagrams**  
   For each diagram in the JSON:  
   - Check `diagram_type`. If it’s `"scale"`, proceed (add logic for other types later).  
   - Create a visual block for the diagram.

4. **Render the Scale**  
   - Draw a scale base with a weight display showing `scale_weight` (e.g., 25, 16).  
   - Add platforms based on `position`:  
     - `center`: One platform in the middle.  
     - `left`/`right`: Two platforms, one on each side (like the last diagram).  

5. **Add Objects to Platforms**  
   For each object in the `objects` array:  
   - Identify the `type` (cube, triangle, weight, circle) and draw that shape.  
   - Repeat the shape based on `number` (e.g., 3 cubes).  
   - Color the shape using `color` (e.g., blue, yellow).  
   - Arrange shapes based on `orientation`:  
     - `vertical`: Stack them upward.  
     - `horizontal`: Place them side by side.  
   - Place the objects on the correct platform (`position`: left, right, or center).  
   - If the object is a weight, show the `weight_value` (e.g., 10, 6) on it.

6. **Style for Clarity**  
   - Style the scale, platforms, and objects to match the look:  
     - Scale: A base with a clear weight display.  
     - Objects: Consistent shapes (e.g., cubes as squares, triangles as triangles) with proper colors.  
     - Platforms: Positioned clearly (left, right, or center).  
   - Add spacing between diagrams for readability.

7. **Handle Future Types**  
   - If `diagram_type` isn’t `"scale"`, prepare to handle other types (e.g., charts) by adding new rendering logic.

### Example for One Diagram
For the first diagram:  
- See `diagram_type: "scale"`, draw a scale.  
- Show `scale_weight: 25` on the scale.  
- Add a central platform (`position: "center"`).  
- Draw 3 blue cubes (`type: "cube"`, `number: 3`, `color: "blue"`) stacked vertically (`orientation: "vertical"`).  
- Add 1 gray weight (`type: "weight"`, `number: 1`, `color: "gray"`) with `weight_value: 10` beside the cubes.

For the last diagram:  
- Draw two scales (one for each `diagram_id`).  
- First scale (`scale_weight: 9`): Left platform with 3 yellow circles (vertical) and a 6-unit weight.  
- Second scale (`scale_weight: 7`): Right platform with 4 yellow circles (horizontal) and 1 red cube.

### Tips
- Keep shapes and colors consistent across diagrams.  
- Ensure diagrams are spaced out for easy viewing.  
- Make it responsive so it looks good on all devices.  
- Plan for new diagram types by checking `diagram_type` first.

This script gives a clear, simplified path for rendering the diagrams while keeping flexibility for future expansions.