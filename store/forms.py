from django import forms
from .models import ReviewRating


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a short title for your review'
            }),
            'review': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your detailed review here...',
                'rows': 4
            }),
            'rating': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'subject': 'Review Title',
            'review': 'Your Review',
            'rating': 'Rating (1–5)',
        }

    def clean_review(self):
        review = self.cleaned_data.get('review')
        if review and len(review.strip()) < 10:
            raise forms.ValidationError("Review must be at least 10 characters long.")
        return review
