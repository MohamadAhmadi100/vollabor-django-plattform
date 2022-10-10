from blog.models import PostComment, Post


def extract_comment_info(post_request):
    name = post_request['name']
    email = post_request['email']
    message = post_request['message']
    return name, email, message


def submit_a_comment(post_request, post):
    name, email, message = extract_comment_info(post_request)
    PostComment(post=post, name=name, email=email, comment=message).save()


def delete_the_post(post_id):
    post = Post.objects.get(id=post_id)
    post.is_deleted = True
    post.save()


def accept_comment(comment_id):
    post_comment = PostComment.objects.get(id=comment_id)
    post_comment.is_verified = True
    post_comment.save()


def delete_comment(comment_id):
    post_comment = PostComment.objects.get(id=comment_id)
    post_comment.is_rejected = True
    post_comment.save()
