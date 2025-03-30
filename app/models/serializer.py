def serialize_post(post):
    return {
        "id": post.id,
        "text": post.text,
        "posted_at": post.posted_at,
        "user": {
            "id": post.user.id,
            "username": post.user.username,
            "image_uuid": post.user.image_uuid
        },
        "images": [{"image": f"https://recomend-iuos.onrender.com/{img.image}"} for img in (post.post_images or [])],
        "likes" : len(post.likes) or 0
    }