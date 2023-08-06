"""Simple markdown generator for Python."""
import yaml
try:
  import markdown
except:  # pylint: disable=W0702
  markdown = None  # pylint: disable=C0103


class NotAllowedException(Exception):
  """Not allowed exception"""


class BadFormatException(Exception):
  """Bad formatting detected"""


class MarkdownElement():
  """Top level markdown element"""

  def __init__(self, objects=None):
    if objects is None:
      objects = []
    self._parent = None
    self.__children = []
    _objects = objects if isinstance(objects, (list)) else [objects] if objects is not None else []
    for _o in _objects:
      self.__add_child(_o)

  def __len__(self):
    return len(self.__children)

  def __repr__(self):
    return self.output

  @property
  def root(self):
    """Returns root element"""
    if self._parent:
      return self._parent.root
    return self

  def _is_parent_class(self, _class):
    """Returns if parent class is of type"""
    if self._parent:
      if isinstance(self._parent, _class):
        return True
      return self._parent._is_parent_class(_class)  # pylint: disable=W0212
    return False

  @property
  def output(self):
    """Returns rendered markdown document"""
    _rv = self._render(None).split("\n")
    _rv = [_ for _lc, _ in enumerate(_rv) if not _lc or len(_) or (len(_rv[_lc - 1]) != len(_))]
    return "\n".join(_rv)

  def write(self, filename):
    """Writes rendered markdown document to a file"""
    try:
      with open(filename, "w", encoding="utf-8") as _f:
        _f.write(self.output)
    except Exception as _e:
      print(f"Unable to write to file {filename}: {_e}")
      raise

  @property
  def _children(self):
    return self.__children

  def __rshift__(self, _p2):
    self.__add_child(_p2)

  def __add_child(self, _child):
    if isinstance(_child, MarkdownElement):
      if _child._parent:  # pylint: disable=W0212
        raise Exception(f"Already has parent: {_child} -> {_child._render(_child._parent)}")  # pylint: disable=W0212,W0719
      _child._parent = self  # pylint: disable=W0212

    elif isinstance(_child, list):
      for _c in _child:
        if isinstance(_c, MarkdownElement):
          if _c._parent:  # pylint: disable=W0212
            raise Exception(f"Already has parent: {_c} -> {_c._render(_c._parent)}")  # pylint: disable=W0212,W0719
          _c._parent = self  # pylint: disable=W0212

    self.__children.append(_child)

  def _render(self, _parent):
    _rv = []
    if isinstance(self, ChildlessMarkdownElement):
      _rv.append(self._render_item(_parent, None, None))
    else:
      _rv += self.__process_render_children(_parent, self.__children)
    return self._render_item_complete(_parent, _rv)

  def __process_render_children(self, parent, children):
    _rv = []
    for _lc, _c in enumerate(children):
      if isinstance(_c, MarkdownElement):
        _r = _c._render(self)  # pylint: disable=W0212
        if _r is not None:
          _ri = self._render_item(parent, _c, _r)
          if _ri:
            _rv.append(_ri)
      else:
        if isinstance(_c, (list)):
          _rv.append(self.__process_render_children(parent, _c))
        elif _c is not None:
          _rv.append(self._render_item(parent, None, _c))
    return _rv

  def _render_item(self, _parent, _child, _item):
    raise NotAllowedException()

  def _render_item_complete(self, _parent, _s):
    return "".join(_s) if isinstance(_s, (list)) else _s


class ChildlessMarkdownElement(MarkdownElement):
  """Childless markdown element (abstract)"""

  def __init__(self, o=None):
    if o is None:
      o = []
    super().__init__(o)

  def __rshift__(self, p2):
    raise NotAllowedException()


class Document(MarkdownElement):
  """Represents the top-level document"""

  def __init__(self, front_matter=None):
    super().__init__()
    self.__front_matter = front_matter
    if front_matter and not isinstance(front_matter, (dict)):
      raise Exception("Invalid front_matter, dictionary only!")  # pylint: disable=W0719

  def _render(self, _parent):
    _rv = super()._render(_parent)
    if self.__front_matter:
      _md = yaml.dump(self.__front_matter, explicit_start=True, explicit_end=True, sort_keys=False)
      return f"{_md}\n{_rv}"
    return _rv

  def _render_item(self, _parent, _child, _item):
    return _item


class Header(ChildlessMarkdownElement):
  """Represents markdown header"""

  def __init__(self, title, level=1):
    super().__init__()
    self.__title = title
    self.__level = level

  def _render_item(self, _parent, _child, _item):
    _pad = "".join("#" for _ in range(self.__level))
    _rv = f"\n{_pad} {self.__title}\n\n"
    return _rv


class Paragraph(MarkdownElement):
  """Represents a paragraph"""

  def __init__(self, o=None):
    super().__init__(o)

  def _render_item(self, _parent, _child, _item):
    return _item

  def _render_item_complete(self, _parent, _s):
    return "\n\n" + " ".join(_s) + "\n"


class Sentence(MarkdownElement):
  """Represents a sentence"""

  def __init__(self, o=None, separator=" ", end="."):
    super().__init__(o)
    self.__separator = separator
    self.__end = end

  def _render_item(self, _parent, _child, _item):
    return _item

  def _render_item_complete(self, _parent, _s):
    return self.__separator.join(_s) + self.__end


class HorizontalRule(ChildlessMarkdownElement):
  """Represents markdown horizontal rule"""

  def __init__(self):
    super().__init__()

  def _render_item(self, _parent, _child, _item):
    return "\n\n---\n\n"


class Link(ChildlessMarkdownElement):
  """Represents markdown link"""

  def __init__(self, title, url, alt_title=None):
    super().__init__()
    self._title = title
    self._url = url
    self._alt_title = alt_title

  def _render_item(self, _parent, _child, _item):
    if isinstance(self._title, MarkdownElement):
      return f'[{self._title._render(self)}]({self._url})'  # pylint: disable=W0212

    if self._alt_title:
      return f'[{self._title}]({self._url} "{self._alt_title}")'
    return f'[{self._title}]({self._url} "{self._title}")'


class Image(Link):
  """Represents markdown image"""

  def __init__(self, title, url):
    super().__init__(title, url)

  def _render_item(self, _parent, _child, _item):
    return f"!{super()._render_item(_parent, _child, _item)}"


class Bold(MarkdownElement):
  """Represents bolded string"""

  def __init__(self, o):
    super().__init__(o)

  def _render_item(self, _parent, _child, _item):
    return f"**{_item}**"


class Italic(MarkdownElement):
  """Represents italicised string"""

  def __init__(self, o):
    super().__init__(o)

  def _render_item(self, _parent, _child, _item):
    return f"*{_item}*"


class BoldItalic(MarkdownElement):
  """Represents bolded/italicised string"""

  def __init__(self, o):
    super().__init__(o)

  def _render_item(self, _parent, _child, _item):
    return f"***{_item}***"


class Strikethrough(MarkdownElement):
  """Represents strikethough string"""

  def __init__(self, o):
    super().__init__(o)

  def _render_item(self, _parent, _child, _item):
    return f"~~{_item}~~"


class Code(MarkdownElement):
  """Represents markdown code string"""

  def __init__(self, o):
    super().__init__(o)

  def _render_item(self, _parent, _child, _item):
    return f"`{_item}`"


class CodeBlock(MarkdownElement):
  """Represents markdown code block"""

  def __init__(self, o=None):
    super().__init__(o)

  def _render_item(self, _parent, _child, _item):
    return _item

  def _render_item_complete(self, _parent, _s):
    return "```\n" + "\n".join(_s) + "\n```\n"


class List(MarkdownElement):
  """Represents markdown parent list (abstract)"""

  def __init__(self, o=None):
    if o is None:
      o = []
    super().__init__(o)

  def _render(self, _parent):
    _rv = super()._render(_parent)
    if isinstance(_parent, Table) or (_parent and _parent._is_parent_class(Table)):  # pylint: disable=W0212
      if markdown:
        return markdown.markdown(_rv, extensions=['attr_list']).replace("\n", "")
      raise BadFormatException(f"Cannot embed List in {_parent.__class__.__name__} without markdown package.")
    return _rv

  def _render_item(self, _parent, _child, _item):
    _pad = "".join(" " for _ in range(self.__check_indent(self) * 3))
    _rv = self._render_list_item(isinstance(_child, (List)), _pad, "".join(_item))
    return _rv

  def _render_list_item(self, _child_is_list, _pad, _item):
    raise NotAllowedException()

  def _render_item_complete(self, _parent, _s):
    if isinstance(_parent, (List)):
      return "\n".join(_s)
    return "\n" + "\n".join(_s) + "\n"

  def __check_indent(self, _o, _count=0):
    if _o._parent:  # pylint: disable=W0212
      _c = _count + 1 if isinstance(_o._parent, List) else _count  # pylint: disable=W0212
      return self.__check_indent(_o._parent, _c)  # pylint: disable=W0212
    return _count


class UnorderedList(List):
  """Represents markdown unordered list"""

  def _render_list_item(self, _child_is_list, _pad, _item):
    if _child_is_list:
      return _item
    return f"{_pad}- {_item}"


class OrderedList(List):
  """Represents markdown ordered list"""

  def _render_list_item(self, _child_is_list, _pad, _item):
    if _child_is_list:
      return _item
    return f"{_pad}1. {_item}"


class Table(MarkdownElement):
  """Represents markdown table"""

  def __init__(self, heading, alignment=None):
    super().__init__()
    if not isinstance(heading, list):
      heading = [heading]
    self.__heading = []
    for _h in heading:
      if isinstance(_h, MarkdownElement):
        self.__heading.append(_h._render(self))
      else:
        self.__heading.append(_h)
    if alignment is None:
      alignment = []
    elif not isinstance(alignment, list):
      alignment = [alignment]
    _lh = len(self.__heading)
    self.__alignment = alignment[0:_lh]
    self.__alignment.extend([next(reversed(alignment), ":-:") for _ in range(_lh - len(alignment))])

  def _render(self, _parent):
    _rv = super()._render(_parent)
    header = "|" + "|".join(list(self.__format_header(x) for x in self.__heading)) + "|"
    alignment = "|" + "|".join(list(f" {_} " for _ in self.__alignment)) + "|"
    if isinstance(_parent, (Table, List)) or (_parent and _parent._is_parent_class((Table, List))):  # pylint: disable=W0212
      if markdown:
        return markdown.markdown(f"{header}\n{alignment}\n{_rv}", extensions=['tables', 'attr_list']).replace("\n", "")
      raise BadFormatException(f"Cannot embed Table in {_parent.__class__.__name__} without markdown package.")
    return f"\n\n{header}\n{alignment}\n{_rv}\n"

  def __format_header(self, _o):
    if _o:
      return f" **{_o}** "
    return ""

  def _render_item(self, _parent, _child, _item):
    return _item

  def _render_item_complete(self, _parent, _s):
    if isinstance(_s, list):
      _rv = ""
      for item in _s:
        _rv += "| " + " | ".join([str(_) for _ in item]) + " |\n"
      return f"{_rv}\n"
    return f"\n'{_s}'"
