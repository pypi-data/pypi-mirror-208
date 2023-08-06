""" Events entitites """

from enum import Enum


class CaseStatus(Enum):
  """ Case status enum """
  PENDING = 'PENDING'
  FOLLOWED = 'FOLLOWED'
  CLOSED = 'CLOSED'


class CaseIgnoredStatus(Enum):
  """
  Case ignore status, will define what kind ignore happened.
  """
  NORMAL = 'NORMAL'
  IGNORED = 'IGNORED'
  PRESSET = 'PRESSET'
  AUTO = 'AUTO'

class Case:
  """
  Case entity definition

  Available attributes
  --------------------
    pk (int): Case ID
    trigger (Trigger): Trigger object that triggered the case
    asset_id (int): Asset ID
    comments list(Comment): List of comments submitted when the case was opened.
    opened_at (datetime): Date of case opening
    closed_at (datetime): Date of case closing
    status (CaseStatus): Case status
    sequence (int): Case sequence
    ignored_status (CaseIgnoredStatus): Case ignored status
  """

  def __init__(
    self,
    pk,
    trigger,
    asset_id,
    opened_at,
    sequence=None,
    closed_at=None,
    comments=[],
    status=CaseStatus.CLOSED,
    ignored_status=CaseIgnoredStatus.NORMAL
  ):
    """ Constructor """
    self.__pk = pk
    self.__trigger = trigger
    self.__asset_id = asset_id
    self.__comments = comments
    self.__opened_at = opened_at
    self.__closed_at = closed_at
    self.__status = status
    self.__sequence = sequence
    self.__ignored_status = ignored_status
  
  @property
  def pk(self):
    """ Case ID """
    return self.__pk
  
  @property
  def trigger(self):
    """ Trigger object that triggered the case """
    return self.__trigger
  
  @property
  def asset_id(self):
    """ Asset ID """
    return self.__asset_id
  
  @property
  def comments(self):
    """ List of comments submitted when the case was opened """
    return self.__comments
  
  @property
  def opened_at(self):
    """ Date of case opening """
    return self.__opened_at
  
  @property
  def closed_at(self):
    """ Date of case closing """
    return self.__closed_at

  @property
  def status(self):
    """ Status """
    return self.__status

  @property
  def sequence(self):
    """ Sequence """
    if (self.__sequence):
      return f'{self.__trigger.code}/{self.__sequence}'
    else:
      return f'GENERIC/{self.__pk}'

  @property
  def ignored_status(self):
    """ Ignored status """
    return self.__ignored_status

  @property
  def __readable(self):
    """ Readable """
    return f'Case(pk={self.__pk}, trigger={self.__trigger}, asset_id={self.__asset_id}, comments={self.__comments}, opened_at={self.__opened_at}, closed_at={self.__closed_at})'
  
  def __str__(self):
    """ Readable property """
    return self.__readable
  
  def __repr__(self):
    """ Readable property """
    return self.__readable
