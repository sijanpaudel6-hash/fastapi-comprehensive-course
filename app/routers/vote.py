from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas, models, oauth2
from sqlmodel import Session
from ..database import get_session, engine

router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, session: Session = Depends(get_session), current_user: int = Depends(oauth2.get_current_user)):
    post = session.get(models.Post, vote.post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {vote.post_id} does not exist")
    vote_query = session.get(models.Vote, (vote.post_id, current_user.id))
    if vote.dir == 1:
        if vote_query:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"user {current_user.id} has already voted on post {vote.post_id}")
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        session.add(new_vote)
        session.commit()
        return {"message": "successfully added vote"}
    else:
        if not vote_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Vote does not exist")
        session.delete(vote_query)
        session.commit()
        return {"message": "successfully deleted vote"}