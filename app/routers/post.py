from fastapi import status, HTTPException, APIRouter, Response, Depends
from sqlmodel import Session, select
from ..database import engine, get_session
from .. import models, oauth2
from typing import Optional
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.get("/", response_model=list[models.PostWithVotes])
def get_posts(session: Session = Depends(get_session), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    statement = select(models.Post).where(models.Post.title.contains(search)).limit(limit).offset(skip)
    # posts = session.exec(statement).all()

    posts = select(models.Post, func.count(models.Vote.post_id)).join(models.Vote, isouter=True).group_by(models.Post.id).where(models.Post.title.contains(search)).limit(limit).offset(skip)
    fetched_posts = session.exec(posts).all()
    result = []
    for post, votes in fetched_posts:
        result.append({
            "post": post,
            "votes": votes
        })

    return result

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_post(post: models.PostCreate, session: Session = Depends(get_session), current_user: int = Depends(oauth2.get_current_user)):
    new_post = models.Post(**post.model_dump())
    new_post.owner_id = current_user.id
    session.add(new_post)
    session.commit()
    session.refresh(new_post)
    return new_post

@router.get("/{id}", response_model=models.PostWithOwnerVotes)
def get_post(id: int, session: Session = Depends(get_session), current_user: int = Depends(oauth2.get_current_user)):
    post = select(models.Post, func.count(models.Vote.post_id)).join(models.Vote, isouter=True).group_by(models.Post.id).where(models.Post.id == id)
    post = session.exec(post).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"post with id: {id} was not found")
    result = {
        "post": post[0],
        "votes": post[1]}
    return result
    

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, session: Session = Depends(get_session), current_user: int = Depends(oauth2.get_current_user)):
    post = session.get(models.Post, id)
    if not post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"post with id: {id} was not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    session.delete(post)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=models.PostPublic)
def update_post(id: int, post: models.PostUpdate, session: Session = Depends(get_session), current_user: int = Depends(oauth2.get_current_user)):
    existing_post = session.get(models.Post, id)
    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    if existing_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    post_data = post.model_dump(exclude_unset=True)
    existing_post.sqlmodel_update(post_data)
    session.add(existing_post)
    session.commit()
    session.refresh(existing_post)
    return existing_post

