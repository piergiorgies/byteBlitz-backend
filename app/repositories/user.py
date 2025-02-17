from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models.mapping import User, UserType
from app.models import Role
from app.schemas import PaginationParams
from app.schemas import UserListResponse, UserResponse, UserCreate, UserUpdate
from app.util.pwd import _hash_password
class UserRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_user_type_by_id(self, user_type_id: int) -> UserType:
        return self.session.query(UserType).filter(UserType.id == user_type_id).first()

    def create(self, user: UserCreate) -> UserResponse:
        """
        Create a new user

        Args:
            user (UserCreate): the user DTO to create

        Returns:
            UserResponse: the created user
        """
        try:
            pass
            hash, salt = _hash_password(user.password)
            user = User(
                username=user.username,
                password_hash=hash,
                salt=salt,
                email=user.email,
                user_type_id=user.user_type_id
            )
            self.session.add(user)
            self.session.commit()
            return UserResponse.model_validate(user)
        
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        
    def update(self, user: UserUpdate, current_user: User) -> UserResponse:
        try:
            db_user: User = self.session.query(User).filter(User.id == user.id).first()
            if not db_user:
                raise ValueError("User not found")
            
            if user.username:
                db_user.username = user.username
            if user.email:
                db_user.email = user.email
            if user.password:
                hash, salt = _hash_password(user.password)
                db_user.salt = salt
                db_user.password_hash = hash
            if user.user_type_id:
                db_user.user_type_id = user.user_type_id
            
            self.session.commit()
            return UserResponse.model_validate(db_user)
        
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        

    def read_me(self, current_user: User) -> User:
        return self.session.query(User).filter(User.id == current_user.id).first()
    
    def read_all(self, pagination: PaginationParams) -> list[User]:
        try:
            judge_type = (
                self.session.query(UserType)
                .filter(UserType.permissions == Role.JUDGE)
                .one_or_none()
            )
            guest_type = (
                self.session.query(UserType)
                .filter(UserType.permissions == Role.GUEST)
                .one_or_none()
            )
            if not judge_type or not guest_type:
                raise ValueError("Required user types not found")
            
            query = self.session.query(User).filter(
                User.deletion_date.is_(None),
                User.user_type_id.notin_([judge_type.id, guest_type.id])
            )
            
            if pagination.search_filter:
                query = query.filter(User.username.ilike(f"%{pagination.search_filter}%"))
            
            count = query.count()
            users = query.limit(pagination.limit).offset(pagination.offset).all()
            
            return UserListResponse(data=[UserResponse.model_validate(user) for user in users], count=count)
        
        except SQLAlchemyError as e:
            raise e