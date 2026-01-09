from django import forms
from .models import MonthlyGoal

class MonthlyGoalForm(forms.ModelForm):
    """月次目標の編集フォーム"""
    class Meta:
        model = MonthlyGoal
        fields = ['goal_text']
        widgets = {
            'goal_text': forms.Textarea(attrs={
                'class': 'w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent',
                'rows': 4,
                'placeholder': '例：売上目標100万円\n笑顔での接客徹底'
            }),
        }
        labels = {
            'goal_text': '目標内容',
        }