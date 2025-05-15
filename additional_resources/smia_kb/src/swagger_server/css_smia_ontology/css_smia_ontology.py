import logging
import os
import sys

import owlready2
from owlready2 import get_ontology, OwlReadyOntologyParsingError, sync_reasoner_pellet, \
    OwlReadyInconsistentOntologyError, ThingClass, Ontology, destroy_entity

from swagger_server.css_smia_ontology.css_ontology_utils import CapabilitySkillOntologyUtils


class CapabilitySkillOntology:
    """
    This class contains related methods of the Capability-Skill ontology.
    """
    _instance = None    # Object for adding Singleton pattern to the class

    def __init__(self):
        self.ontology: Ontology = None

    @staticmethod
    def get_instance():
        """
        This method implements the Singleton pattern to this class, in order to be available to all controllers.
        """
        if CapabilitySkillOntology._instance is None:
            CapabilitySkillOntology._instance = CapabilitySkillOntology()
        return CapabilitySkillOntology._instance

    def get_ontology(self):
        """
        This method returns the ontology OWLReady2 Python object.

        Returns:
            Ontology: ontology object
        """
        return self.ontology

    def get_namespace(self, namespace):
        """
        This method returns the namespace within the loaded ontology.

        Returns:
            namespace.Ontology: namespace ontology object
        """
        return self.ontology.get_namespace(namespace)

    def initialize_ontology(self):
        """
        This method initializes the Capability-Skill ontology loading the definition of the OWL ontology in the file
        stored in the config folder.
        """

        # Import only ontologies in RDF/XML, OWL/XML or NTriples format (others do not work, e.g. Turtle)

        self.ontology = get_ontology(CapabilitySkillOntologyUtils.get_ontology_file_path())
        try:
            self.ontology.load()
        except FileNotFoundError as e:
            self.ontology = None
            print("ERROR: The OWL file of the ontology does not exist.", file=sys.stderr)
        except OwlReadyOntologyParsingError as e:
            if 'NTriples' in e.args[0]:
                print("ERROR: The OWL file is invalid (only RDF/XML, OWL/XML or NTriples format are accepted).", file=sys.stderr)
            if 'Cannot download' in e.args[0]:
                print("ERROR: The OWL has defined imported ontologies that cannot be downloaded.", file=sys.stderr)
            self.ontology = None
            return
        # The ontology has been loaded
        print("CSS ontology initialized")

    def execute_ontology_reasoner(self, debug=False):
        """
        This method executes the reasoner for the ontology.

        Args:
            debug (bool): if it is true, the inconsistency of the ontology is explained.
        """
        debug_value = 1
        if debug is True:
            debug_value = 2

        try:
            with self.ontology:
                sync_reasoner_pellet(debug=debug_value)
        except OwlReadyInconsistentOntologyError as e:
            print("ERROR: INCONSISTENT ONTOLOGY! {}".format(e), file=sys.stderr)
            raise OwlReadyInconsistentOntologyError(e)

    def get_ontology_class_by_iri(self, class_iri):
        """
        This method gets the class within the ontology by its IRI.

        Args:
            class_iri (str): the IRI of the class to be found.

        Returns:
            object: ontology class object.
        """
        result_classes = self.ontology.search(iri=class_iri)
        if len(result_classes) == 0:
            print("ERROR: class not found with IRI [{}]".format(class_iri), file=sys.stderr)
            return None
        if len(result_classes) > 1:
            print("WARNING: THERE IS MORE THAN ONE CLASS WITH IRI [{}], BE CAREFUL".format(class_iri))
        return result_classes[0]

    def create_ontology_object_instance(self, class_object, instance_name):
        """
        This method creates a new object instance (individual) within the ontology. To this end, a ThingClass is
        required.
        
        Args:
            class_object (ThingClass): ontology class of the instance.
            instance_name (str): name of the instance.

        Returns:
            ThingClass: created instance object.
        """
        if not isinstance(class_object, ThingClass):
            print("ERROR: the instance cannot be created because the given constructor is not of ThingClass.",
                  file=sys.stderr)
        else:
            # The object of the class is used as constructor of the instance
            return class_object(instance_name)

    def get_ontology_instance_by_name(self, instance_name):
        """
        This method returns an object instance within the ontology by its name.

        Args:
            instance_name (str): name of the instance.

        Returns:
            ThingClass: class of the instance to be found (None if it is not found).
        """
        for instance_class in self.ontology.individuals():
            if instance_class.name == instance_name:
                return instance_class
        return None

    def get_ontology_instance_by_iri(self, instance_iri):
        """
        This method returns an object instance within the ontology by its IRI.

        Args:
            instance_iri (str): IRI of the instance.

        Returns:
            ThingClass: class of the instance to be found (None if it is not found).
        """
        for instance_class in self.ontology.individuals():
            if instance_class.iri == instance_iri:
                return instance_class
        return None

    def get_ontology_instances_by_class_iri(self, class_iri):
        """
        This method gets all the instances within the ontology with a given class IRI.

        Args:
            class_iri (str): the IRI of the class to be found.

        Returns:
            list: list of ontology instance objects.
        """
        instances_list = []
        for instance in self.ontology.individuals():
            for parent_class in instance.is_a:
                if parent_class.iri == class_iri:
                    instances_list.append(instance)
        if len(instances_list) == 0:
            return None
        return instances_list

    def delete_ontology_instance(self, instance_object):
        """
        This method deletes an instance from the ontology.

        Args:
            instance_object (ThingClass): instance to delete.
        """
        owlready2.destroy_entity(instance_object)

    def add_object_property_to_instances_by_names(self, object_property_name, domain_object_name, range_object_name):
        """
        This method adds a new ObjectProperty to link two instances within the ontology. Checks are performed to ensure
        that the ObjectProperty is valid to link the instances.

        Args:
            object_property_name (str): name of the ObjectProperty to be added.
            domain_object_name (str): name of the instance to which the ObjectProperty will be added.
            range_object_name (str): name of the instance to be added to the domain instance within the given property.
        """
        # Preliminary checks are performed
        if domain_object_name is None or range_object_name is None:
            print("ERROR: The object property cannot be added because the domain or range are invalid.",
                  file=sys.stderr)
        domain_instance = self.get_ontology_instance_by_name(domain_object_name)
        range_instance = self.get_ontology_instance_by_name(range_object_name)
        try:
            getattr(domain_instance, object_property_name).append(range_instance)
        except AttributeError as e:
            print("ERROR: The class {} does not have the attribute {}".format(domain_instance,
                                                                              object_property_name), file=sys.stderr)


    def get_all_subclasses_iris_of_class(self, owl_class):
        """
        This method gets all IRIs of the subclasses of a given OWL class.

        Args:
            owl_class (ThingClass): OWL class of which the subclasses are to be found.

        Returns:
            list(str): list of IRIs of the subclasses of the given OWL class.
        """
        subclasses = list(owl_class.subclasses())
        all_subclasses_iris = [subclass.iri for subclass in subclasses]
        # The method need to be executed recursively to get all existing subclasses
        for subclass in subclasses:
            all_subclasses_iris.extend(self.get_all_subclasses_iris_of_class(subclass))
        return all_subclasses_iris


    def persistent_save_ontology(self):
        """
        This method saves all the ontological data in a persistent way: in a SQLite3 database file.
        """
        ontology_persistence_file_path = '../css_smia_ontology/persistence.sqlite3'     # TODO PENSAR SI DEJAR COMO OPCION EL PODER DECIDIR DONDE GUARDARLO (p.e. con variable de entorno en Docker)
        try:
            if os.path.isfile(ontology_persistence_file_path):
                print('A SQLite file already exists, so it will be deleted so that it can be updated.')
                os.remove(ontology_persistence_file_path)

            self.ontology.world.set_backend(filename='./persistence.sqlite3')
            self.ontology.world.save()
            print("OWL information saved in SQLite.")
        except Exception as e:
            if sys.platform == 'win32':
                # Using Windows it cannot save in SQLite because of the internal logic of OWLReady2
                pass
            else:
                print("Some error occured, so it cannot saved ontological information in SQLite:", e)