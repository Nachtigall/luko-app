from datetime import datetime

from sqlalchemy.orm import relationship

from app import db


class Letter(db.Model):
    __tablename__ = "letter"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tracking_number = db.Column(db.String(256))
    status = relationship("LetterStatusHistory", cascade="all,delete", backref="letter")

    def serialize(self):
        status_history = [status.serialize() for status in self.status]
        return {
            "tracking_number": self.tracking_number,
            "status_history": sorted(
                status_history, key=lambda sh: sh["modification_date"], reverse=True
            ),
        }


class LetterStatusHistory(db.Model):
    __tablename__ = "letter_status_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    letter_id = db.Column(db.Integer, db.ForeignKey("letter.id", ondelete="CASCADE"))
    status = db.Column(db.String(256), default="New", nullable=False)
    last_update = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    db.UniqueConstraint(letter_id, last_update)

    def serialize(self):
        return {
            "status": self.status,
            "modification_date": self.last_update.strftime("%d.%m.%Y, %H:%M:%S"),
        }
