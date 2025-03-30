def serialize_post(post):
    return {
        "id": post.id,
        "text": post.text,
        "posted_at": post.posted_at,
        "user": {
            "id": post.user.id,
            "username": post.user.username,
            "image_uuid": f"https://auth-wytb.onrender.com/api/v1/image/{post.user.image_uuid}"
        },
        "images": [{"image": img.image} for img in (post.post_images or [])],
        "likes" : len(post.likes) or 0
    }