from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name
    
class Member(models.Model):
    group = models.ForeignKey(Group, related_name='members', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)


    def __str__(self):
        return f"{self.name} ({self.group.name})"    


class Expense(models.Model):
    group = models.ForeignKey(Group, related_name='expenses', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_by = models.ForeignKey(Member, related_name='paid_expenses', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)
    is_custom_split = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.title} - {self.amount}"
    

class ExpenseShare(models.Model):
    expense = models.ForeignKey(Expense, related_name='shares', on_delete=models.CASCADE)
    member = models.ForeignKey(Member, related_name='shares', on_delete=models.CASCADE)
    share_amount = models.DecimalField(max_digits=12, decimal_places=2)


    class Meta:
        unique_together = ('expense', 'member')


    def __str__(self):
        return f"{self.member.name}: {self.share_amount}"
    
    