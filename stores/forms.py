from django import forms
from .models import MonthlyGoal

class MonthlyGoalForm(forms.ModelForm):
    """月次目標の編集フォーム（達成率・状況も含む）"""
    class Meta:
        model = MonthlyGoal
        # ▼▼▼ 達成率と達成状況を追加 ▼▼▼
        fields = ['goal_text', 'achievement_rate', 'achievement_text']
        
        widgets = {
            'goal_text': forms.Textarea(attrs={
                'class': 'w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent',
                'rows': 4,
                'placeholder': '例：売上目標100万円\n笑顔での接客徹底'
            }),
            # ▼▼▼ 追加: 達成率（数値入力） ▼▼▼
            'achievement_rate': forms.NumberInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent',
                'min': '0',
                'max': '100',
                'placeholder': '0〜100'
            }),
            # ▼▼▼ 追加: 達成状況（テキストエリア） ▼▼▼
            'achievement_text': forms.Textarea(attrs={
                'class': 'w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent',
                'rows': 2,
                'placeholder': '例：順調に進んでいます。\n後半で挽回し達成しました。'
            }),
        }
        labels = {
            'goal_text': '目標内容',
            'achievement_rate': '達成率 (%)',
            'achievement_text': '達成状況コメント',
        }