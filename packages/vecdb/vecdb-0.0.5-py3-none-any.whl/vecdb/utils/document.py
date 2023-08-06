import re
import uuid
import pprint
import warnings
import itertools

from typing import Optional, Any, Dict, List, Union
from copy import deepcopy
from collections import UserDict, UserList

from vecdb.utils import json_encoder


class DocumentList(UserList):
    data: List["Document"]

    def __init__(self, initlist=None):
        if initlist is not None:
            for index, document in enumerate(initlist):
                if not isinstance(document, Document):
                    initlist[index] = Document(document)
        super().__init__(initlist)

    def __repr__(self):
        return pprint.pformat(self.to_json(), indent=4, width=40)

    def __getitem__(self, key: Union[str, int]) -> "Document":
        if isinstance(key, str):
            return [document[key] for document in self.data]
        elif isinstance(key, slice):
            return self.__class__(self.data[key])
        elif isinstance(key, int):
            return self.data[key]

    def __setitem__(self, key: Union[str, int], value: Union[Any, List[Any]]):
        if isinstance(key, str):
            if isinstance(value, list):
                for document, value in zip(self.data, value):
                    document[key] = value
            else:
                for document in self.data:
                    document[key] = value
        elif isinstance(key, int):
            self.data[key] = value

    def to_json(self):
        return [document.to_json() for document in self.data]

    def _flatten_list(self, list_of_lists):
        flat_list = itertools.chain(*list_of_lists)
        return list(flat_list)

    def set_chunk_values(self, chunk_field: str, output_field: str, chunk_values: List[List[Any]], sortby: str = None):
        if sortby is None:
            if any("_order_" in key for key in self.data[0].keys()):
                sortby = "_order_"

        assert len(chunk_values) == len(
            self.data
        ), "The length of your values array should be the same as your documents"

        for document, chunk_labels in zip(self.data, chunk_values):
            if chunk_field not in document:
                document[chunk_field] = []

            chunk = document[chunk_field]

            if chunk:
                if sortby is not None:
                    chunk = list(sorted(chunk, key=lambda x: x[sortby]))
                assert len(chunk) == len(
                    chunk_labels
                ), "The length of your `chunk` array should be the same as your `chunk_values`"
                for chunk_index in range(len(chunk_labels)):
                    subchunk = Document(chunk[chunk_index])
                    label = chunk_labels[chunk_index]
                    subchunk[output_field] = label
                    chunk[chunk_index] = subchunk.to_json()
            else:
                document[chunk_field] = chunk_labels

    def set_chunks_from_flat(self, chunk_field: str, field: str, values: list):
        """
        Set chunks from a flat list.
        Note that this is only possible if there is pre-existing
        chunk documents.
        """
        # general logic for this is that we assume that the number of values equals
        # to the number of chunk values
        chunk_counter = 0
        for i, doc in enumerate(self.data):
            chunk_docs = []
            for j, chunk_doc in enumerate(doc.get(chunk_field, [])):
                # chunk_doc = Document(chunk_doc)
                chunk_doc = Document(chunk_doc)
                chunk_doc.set(field, values[chunk_counter])
                chunk_docs.append(chunk_doc)
                chunk_counter += 1
            doc.set(chunk_field, chunk_docs)

        if chunk_counter > len(values):
            raise ValueError("Number of chunks do not match with number of values - check logic.")

    def get_chunks_as_flat(self, chunk_field: str, field: str, default=None):
        """
        Set chunks from a flat list.
        Note that this is only possible if there is pre-existing
        chunk documents.
        """
        docs = DocumentList(self._flatten_list([d.get(chunk_field) for d in self.data]))
        return [d.get(field, default=default) for d in docs.data]

    def split_by_chunk(self, chunk_field: str, values: list):
        """
        Split a list of values based on the number of documents
        within a specific chunk field
        """
        counter = 0
        for d in self.data:
            chunk_field_len = len(d.get(chunk_field, []))
            yield values[counter : counter + chunk_field_len]
            counter += len(d.get(chunk_field, []))

    def remove_tag(self, field: str, value: str) -> None:
        warnings.warn("This behaviour is experimental and is subject to change")

        *tag_fields, remove_field = field.split(".")
        tag_field = ".".join(tag_fields)

        for document in self.data:
            new_tags = []

            old_tags = document.get(tag_field, [])
            for tag_json in old_tags:
                if tag_json.get(remove_field) != value:
                    new_tags.append(tag_json)

            document[tag_field] = new_tags

    def append_tag(self, field: str, value: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        warnings.warn("This behaviour is experimental and is subject to change")

        if isinstance(value, list):
            for document, tag in zip(self.data, value):
                document[field].append(tag)
        else:
            for document in self.data:
                document[field].append(value)

    def sort_tags(self, field: str, reverse: bool = False) -> None:
        warnings.warn("This behaviour is experimental and is subject to change")

        *tag_fields, sort_field = field.split(".")
        tag_field = ".".join(tag_fields)

        for document in self.data:
            tags = document.get(tag_field)

            if tags is not None:
                document[tag_field] = sorted(
                    document[tag_field], key=lambda tag_json: tag_json[sort_field], reverse=reverse
                )


class Document(UserDict):
    def __repr__(self):
        return pprint.pformat(self.data, indent=4)

    def __setitem__(self, key: Any, value: Any) -> None:
        try:
            fields = key.split(".")
        except:
            super().__setitem__(key, value)
        else:
            obj = self.data
            for curr_field, next_field in zip(fields, fields[1:]):
                if curr_field.isdigit():
                    curr_field = int(curr_field)

                if (isinstance(obj, dict) and (curr_field not in obj)) or (
                    isinstance(obj, list) and (curr_field >= len(obj))
                ):
                    if next_field.isdigit():
                        obj[curr_field] = [{}]
                    else:
                        if isinstance(curr_field, int):
                            curr_field = min(len(obj) - 1, int(curr_field))
                            if next_field not in obj[curr_field]:
                                obj[curr_field] = {}
                        else:
                            obj[curr_field] = {}

                try:
                    obj = obj[curr_field]
                except IndexError:
                    obj = obj[0]
                except KeyError:
                    obj = obj[curr_field]

            if fields[-1].isdigit():
                field = min(len(obj) - 1, int(fields[-1]))
            else:
                field = fields[-1]
            obj[field] = value

    def __getitem__(self, key: Any) -> Any:
        try:
            fields = key.split(".")
        except:
            return super().__getitem__(key)
        else:
            obj = self.data
            for field in fields[:-1]:
                if field.isdigit():
                    field = int(field)

                obj = obj[field]

            if fields[-1].isdigit():
                field = min(len(obj) - 1, int(fields[-1]))
            else:
                field = fields[-1]
            return obj[field]

    def __delitem__(self, key):
        try:
            fields = key.split(".")
        except:
            return super().__getitem__(key)
        else:
            obj = self.data
            for field in fields[:-1]:
                if field.isdigit():
                    field = int(field)

                obj = obj[field]

            if fields[-1].isdigit():
                field = min(len(obj) - 1, int(fields[-1]))
            else:
                field = fields[-1]
            del obj[field]

    def get(self, key: Any, default: Optional[Any] = None) -> Any:
        try:
            return self.__getitem__(key)
        except:
            return default

    def set(self, key: Any, value: Any) -> None:
        self.__setitem__(key, value)

    def keys(self):
        def get_keys(dictionary: Dict[str, Any], prefix=""):
            keys = []
            for key, value in dictionary.items():
                current_key = prefix + "." + key if prefix else key
                if isinstance(value, dict):
                    keys.extend(get_keys(value, current_key))
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            keys.extend(get_keys(item, current_key + "." + str(i)))
                    keys.append(current_key)
                else:
                    keys.append(current_key)
            if prefix:
                keys.append(prefix)
            return keys

        keys = set(get_keys(self.data))

        keys_to_add = set()
        for key in keys:
            subkeys = key.split(".")
            for i in range(1, len(subkeys)):
                keys_to_add.add(".".join(subkeys[:i]))
        keys.update(keys_to_add)

        return list(sorted(keys))

    def __contains__(self, key) -> bool:
        return key in self.keys()

    def to_json(self):
        return json_encoder.json_encoder(deepcopy(self.data))

    def list_chunks(self):
        """
        List the available chunks inside of the document.
        """
        # based on conversation with API team
        return [k for k in self.keys() if k.endswith("_chunk_")]

    def get_chunk(self, chunk_field: str, field: str = None, default: str = None):
        """
        Returns a list of values.
        """
        # provide a recursive implementation for getting chunks

        document_list = DocumentList(self.get(chunk_field, default=default))
        # Get the field across chunks
        if field is None:
            return document_list
        return [d.get(field, default=default) for d in document_list.data]

    def _create_chunk_documents(self, field: str, values: list, generate_id: bool = False):
        """
        create chunk documents based on a given field and value.
        """

        if generate_id:
            docs = [{"_id": uuid.uuid4().__str__(), field: values[i], "_order_": i} for i in range(len(values))]
        else:
            docs = [{field: values[i], "_order_": i} for i in range(len(values))]
        return DocumentList(docs)

    def _calculate_offset(self, text_to_find, string):
        try:
            result = [{"start": m.start(), "end": m.end()} for m in re.finditer(text_to_find, string)]
        except Exception as e:
            import traceback

            traceback.print_exc()
            # this is the error this exception aims to solve
            #     for m in re.finditer(text_to_find, string)
            #     return _compile(pattern, flags).finditer(string)
            #     p = sre_compile.compile(pattern, flags)
            #     p = sre_parse.parse(p, flags)
            #     p = _parse_sub(source, state, flags & SRE_FLAG_VERBOSE, 0)
            #     itemsappend(_parse(source, state, verbose, nested + 1,
            #     raise source.error("nothing to repeat",
            # re.error: nothing to repeat at position 0
            # instead, we will use fuzzysearch
            from fuzzysearch import find_near_matches

            matches = find_near_matches(text_to_find, string, max_l_dist=2)
            result = [{"start": m.start, "end": m.end} for m in matches]
        return result

    def set_chunk(self, chunk_field: str, field: str, values: list, generate_id: bool = False):
        """
        doc.list_chunks()
        doc.get_chunk("value_chunk_", field="sentence") # returns a list of values
        doc.set_chunk("value_chunk_", field="sentence", values=["hey", "test"])
        """
        new_chunk_docs = self._create_chunk_documents(field, values=values, generate_id=generate_id)
        # Update on the old chunk docs
        old_chunk_docs = DocumentList(self.get(chunk_field))
        # Relying on immutable property
        [d.update(new_chunk_docs[i]) for i, d in enumerate(old_chunk_docs.data)]

    def split(
        self,
        split_operation: callable,
        chunk_field: str,
        field: str,
        default: Any = None,
        include_offsets: bool = True,
        generate_id: bool = False,
    ):
        """
        The split operation is as follows:

        The split operation returns to us a list of possible values.
        The chunk documents are then created automatically for you.
        """
        if default is None:
            default = []
        value = self.get(field, default)
        split_values = split_operation(value)
        chunk_documents = self._create_chunk_documents(field=field, values=split_values, generate_id=generate_id)

        if include_offsets:
            for i, d in enumerate(chunk_documents):
                offsets = self._calculate_offset(d[field], value)
                d["_offsets_"] = offsets

        self.set(chunk_field, chunk_documents)

    def operate_on_chunk(
        self, operator_function: callable, chunk_field: str, field: str, output_field: str, default: Any = None
    ):
        """
        Add an operate function.
        """
        values = self.get_chunk(chunk_field=chunk_field, field=field, default=default)
        results = operator_function(values)
        self.set_chunk(chunk_field=chunk_field, field=output_field, values=results)
