import abc
import typing

from hpotk.algorithm import get_ancestors
from hpotk.model import Identified, TermId
from hpotk.ontology import MinimalOntology
from hpotk.constants.hpo.base import PHENOTYPIC_ABNORMALITY

from ._model import ValidationResult, ValidationResults, ValidationLevel, RuleValidator


class BaseOntologyRuleValidator(RuleValidator, metaclass=abc.ABCMeta):

    def __init__(self, ontology: MinimalOntology):
        if not isinstance(ontology, MinimalOntology):
            raise ValueError(f'ontology must be an instance of hpotk.ontology.MinimalOntology '
                             f'but it was an instance of {type(ontology)}')
        self._ontology = ontology

    def _primary_term_id(self, identifier: TermId) -> typing.Optional[TermId]:
        """
        Map the provided `identifier` into the primary term ID in case the `identifier` is obsolete.
        """
        current_term = self._ontology.get_term(identifier)
        return current_term.identifier if current_term is not None else None


class AnnotationPropagationValidator(BaseOntologyRuleValidator):
    """
    Validator to check that a sequence of terms does not contain a term and its ancestor.

    The validator replaces obsolete term IDs with the current term IDs before performing the validation.
    """

    def __init__(self, ontology: MinimalOntology):
        super().__init__(ontology)

    def validate(self, items: typing.Sequence[typing.Union[Identified, TermId]]) -> ValidationResults:
        term_ids = {self._primary_term_id(self.extract_term_id(item)) for item in items}
        results = []
        for term_id in term_ids:
            for ancestor in get_ancestors(self._ontology, source=term_id, include_source=False):
                if ancestor in term_ids:
                    current_term = self._ontology.get_term(term_id)
                    ancestor_term = self._ontology.get_term(ancestor)
                    results.append(
                        ValidationResult(level=ValidationLevel.ERROR,
                                         category='annotation_propagation',
                                         message=f'Terms should not contain both '
                                                 f'{current_term.name} [{current_term.identifier.value}] '
                                                 f'and its ancestor '
                                                 f'{ancestor_term.name} [{ancestor_term.identifier.value}]'))

        return ValidationResults(results)


class PhenotypicAbnormalityValidator(BaseOntologyRuleValidator):
    """
    Validator for checking that the term is a phenotypic abnormality
    (a descendant of Phenotypic abnormality HP:0000118).

    The validator replaces obsolete term IDs with the current term IDs before performing the validation.
    """

    def __init__(self, ontology: MinimalOntology):
        super().__init__(ontology)

    def validate(self, items: typing.Sequence[typing.Union[Identified, TermId]]) -> ValidationResults:
        results = []
        for item in items:
            term_id = self.extract_term_id(item)
            term_id = self._primary_term_id(term_id)
            ancestors = get_ancestors(self._ontology, source=term_id, include_source=False)
            if PHENOTYPIC_ABNORMALITY not in ancestors:
                item = self._ontology.get_term(term_id)
                results.append(
                    ValidationResult(
                        level=ValidationLevel.ERROR,
                        category='phenotypic_abnormality_descendant',
                        message=f'{item.name} [{item.identifier.value}] '
                                f'is not a descendant of Phenotypic abnormality [{PHENOTYPIC_ABNORMALITY.value}]'
                    )
                )

        return ValidationResults(results)


class ObsoleteTermIdsValidator(BaseOntologyRuleValidator):

    def __init__(self, ontology: MinimalOntology):
        super().__init__(ontology)

    def validate(self, items: typing.Sequence[typing.Union[Identified, TermId]]) -> ValidationResults:
        results = []
        for item in items:
            term_id = self.extract_term_id(item)
            current_id = self._primary_term_id(term_id)
            if current_id != term_id:
                current_term = self._ontology.get_term(current_id)
                results.append(
                    ValidationResult(
                        level=ValidationLevel.WARNING,
                        category='obsolete_term_id_is_used',
                        message=f'Using the obsolete {term_id} instead of {current_id.value} '
                                f'for {current_term.name}'
                    )
                )

        return ValidationResults(results)
