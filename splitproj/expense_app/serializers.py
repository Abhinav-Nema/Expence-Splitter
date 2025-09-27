from rest_framework import serializers
from .models import Group, Member, Expense, ExpenseShare


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'name', 'email', 'group']
        read_only_fields = ['id']


class ExpenseShareSerializer(serializers.ModelSerializer):
    member = serializers.PrimaryKeyRelatedField(queryset=Member.objects.all())


    class Meta:
        model = ExpenseShare
        fields = ['id', 'member', 'share_amount']
        read_only_fields = ['id']



class ExpenseSerializer(serializers.ModelSerializer):
    paid_by = serializers.PrimaryKeyRelatedField(queryset=Member.objects.all())
    shares = ExpenseShareSerializer(many=True, required=False)


    class Meta:
        model = Expense
        fields = ['id', 'group', 'title', 'amount', 'paid_by', 'is_custom_split', 'shares', 'note', 'created_at']
        read_only_fields = ['id', 'created_at']


    def create(self, validated_data):
        shares_data = validated_data.pop('shares', None)
        expense = Expense.objects.create(**validated_data)


        if not shares_data:
            members = expense.group.members.all()
            if not members:
                raise serializers.ValidationError("Group has no members")
            equal_share = expense.amount / members.count()
            for m in members:
                ExpenseShare.objects.create(expense=expense, member=m, share_amount=equal_share)
            return expense


        total = sum([float(s['share_amount']) for s in shares_data])
        if round(total, 2) != round(float(expense.amount), 2):
            raise serializers.ValidationError('Custom shares do not sum to total amount')


        for s in shares_data:
            ExpenseShare.objects.create(expense=expense, member=s['member'], share_amount=s['share_amount'])
        return expense
    

    
class GroupSerializer(serializers.ModelSerializer):
    members = MemberSerializer(many=True, read_only=True)
    expenses = ExpenseSerializer(many=True, read_only=True)


    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'created_at', 'members', 'expenses']
        read_only_fields = ['id', 'created_at']    