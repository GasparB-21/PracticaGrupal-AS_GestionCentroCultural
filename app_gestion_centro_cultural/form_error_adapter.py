class FormErrorAdapter:
    def __init__(self, form):
        self.form = form
 
    def get_field_errors(self):
        if not self.form.errors:
            return {}
            
        field_errors = {}
        for field_name, errors in self.form.errors.items():
            if field_name != '__all__':
                label = self.form.fields[field_name].label if field_name in self.form.fields else field_name
                field_errors[label] = list(errors)
        return field_errors
 
    def get_global_errors(self):
        return list(self.form.errors.get('__all__', []))
 
    def has_errors(self):
        return self.form.is_bound and bool(self.form.errors)