class VisionFusion:
    def fuse(
        self,
        classical_result: dict,
        yolo_result: dict
    ) -> dict:
        width = classical_result["width"]
        height = classical_result["height"]
        image_area = width * height

        people = yolo_result["people"]

        total_people_area = 0

        for person in people:
            bbox = person["bbox"]

            person_width = bbox[2] - bbox[0]
            person_height = bbox[3] - bbox[1]

            person_area = max(0, person_width * person_height)
            total_people_area += person_area

        prominence = 0.0

        if image_area > 0:
            prominence = total_people_area / image_area

        return {
            "people_count": yolo_result["people_count"],
            "people_prominence": round(
                min(prominence, 1.0),
                4
            ),
            "image_quality": self.calculate_image_quality(
                classical_result
            ),
            "brightness": classical_result["brightness"],
            "contrast": classical_result["contrast"],
            "sharpness": classical_result["sharpness"],
            "edge_density": classical_result["edge_density"],
            "contours": classical_result["contours"],
            "width": width,
            "height": height
        }

    def calculate_image_quality(
        self,
        classical_result: dict
    ) -> float:
        sharpness = classical_result["sharpness"]
        contrast = classical_result["contrast"]

        sharpness_score = min(sharpness / 500, 1.0)
        contrast_score = min(contrast / 100, 1.0)

        score = (
            sharpness_score * 0.6
            + contrast_score * 0.4
        ) * 100

        return round(score, 2)