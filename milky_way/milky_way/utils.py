from django.contrib import admin



class BaseAdmin(admin.ModelAdmin):
    save_as = True
    save_on_top = True


class CustomStr:
    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        elif hasattr(self, 'title'):
            return self.title
        elif hasattr(self, 'currency') and hasattr(self, 'payment_type'):
            return f'{self.currency} - {self.payment_type}'
        else:
            return str(self.id)
