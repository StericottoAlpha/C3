from django import template

register = template.Library()

@register.simple_tag
def is_reacted(post, user, reaction_type):
    if not user.is_authenticated:
        return False
    return post.reactions.filter(user=user, reaction_type=reaction_type).exists()

@register.simple_tag
def count_reactions(post, reaction_type):
    return post.reactions.filter(reaction_type=reaction_type).count()


@register.simple_tag
def is_comment_reacted(comment, user, reaction_type):

    if not user.is_authenticated:
        return False
    return comment.reactions.filter(user=user, reaction_type=reaction_type).exists()

@register.simple_tag
def count_comment_reactions(comment, reaction_type):
    return comment.reactions.filter(reaction_type=reaction_type).count()