from rest_framework import serializers


class UploadSerializer(serializers.Serializer):
    """
    Validates POST /api/analyze/
    Accepts any combination of PDF files and/or plain text.
    """
    resume          = serializers.FileField(required=False)
    job_description = serializers.FileField(required=False)
    resume_text     = serializers.CharField(required=False, allow_blank=True)
    jd_text         = serializers.CharField(required=False, allow_blank=True)

    def validate_resume(self, value):
        if value is None:
            return value
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError(
                "Resume must be a PDF file. Got: " + value.name
            )
        if value.size == 0:
            raise serializers.ValidationError("Resume file is empty.")
        return value

    def validate_job_description(self, value):
        if value is None:
            return value
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError(
                "Job Description must be a PDF file. Got: " + value.name
            )
        if value.size == 0:
            raise serializers.ValidationError("Job Description file is empty.")
        return value

    def validate(self, data):
        """
        Each side (resume + JD) must have either a file OR text.
        Mixed input is allowed — e.g. PDF resume + text JD.
        """
        has_resume = data.get('resume') or data.get('resume_text', '').strip()
        has_jd     = data.get('job_description') or data.get('jd_text', '').strip()

        if not has_resume:
            raise serializers.ValidationError(
                "Please provide your resume — either upload a PDF or paste the text."
            )
        if not has_jd:
            raise serializers.ValidationError(
                "Please provide the job description — either upload a PDF or paste the text."
            )
        return data