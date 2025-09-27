from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Group, Member, Expense
from .serializers import GroupSerializer, MemberSerializer, ExpenseSerializer
from .utils import calculate_group_overview, settle_group_balances



class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


    @action(detail=True, methods=['get'])
    def overview(self, request, pk=None):
        group = self.get_object()
        return Response(calculate_group_overview(group))


    @action(detail=True, methods=['get'])
    def settle(self, request, pk=None):
        group = self.get_object()
        return Response({'transactions': settle_group_balances(group)})
    

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer


    def get_queryset(self):
        qs = super().get_queryset()
        group_id = self.request.query_params.get('group')
        if group_id:
            qs = qs.filter(group_id=group_id)
        return qs
    

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer


    def get_queryset(self):
        qs = super().get_queryset()
        group_id = self.request.query_params.get('group')
        if group_id:
            qs = qs.filter(group_id=group_id)
        return qs