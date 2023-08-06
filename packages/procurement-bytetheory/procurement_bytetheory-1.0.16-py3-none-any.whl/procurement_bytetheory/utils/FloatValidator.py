from prompt_toolkit.validation import ValidationError, Validator


class FloatValidator(Validator):
    def validate(self, document):
        try:
            float(document.text)
        except:
            raise ValidationError(
                message="Please enter a valid number",
                cursor_position=len(document.text),
            )  # Move cursor to end
