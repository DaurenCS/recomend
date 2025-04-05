def serialize_post(post, user_id):
    is_liked = any(like.user_id == user_id for like in post.likes) if post.likes else False

    return {
        "id": post.id,
        "text": post.text,
        "posted_at": post.posted_at,
        "user": {
            "id": post.user.id ,
            "username": post.user.username ,
            "image_uuid": f"https://auth-wytb.onrender.com/api/v1/image/{post.user.image_uuid}" 
        } if post.user else None,
        "organization" : {
            "id": post.organization.id,
            "name": post.organization.name,
            "image": post.organization.image,
        }if post.organization else None,
        "images": [{"image": img.image} for img in (post.post_images or [])],
        "likes" : len(post.likes) or 0,
        "is_liked": is_liked
    }

def serialize_event(event):
    return {
        "id": event.id,
        "organization" : {
            "id": event.organization.id,
            "name": event.organization.name,
            "image": event.organization.image,
        },
        "name": event.name,
        "created_at": event.created_at,
        "image": event.image,
        "price": event.price,
        "additional": event.additional,
        "location": event.location,
        "date": event.date,
        "description": event.description

    }