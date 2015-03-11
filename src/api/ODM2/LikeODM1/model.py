from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property, relationship
from sqlalchemy import select, MetaData, Integer, String, Column, ForeignKey, DateTime, Float

Base = declarative_base()

metadata = MetaData()

################ODM 2 Tables###########
from ..model import Actions, Organizations, Affiliation, People, \
    Samplingfeatures, Results, Variables, Methods, Timeseriesresult, \
    Timeseriesresultvalue, Site, SpatialReference, CVTerms

action_table = Actions()

# ###################################################################################
#                           Monitoring Site Locations
# ###################################################################################


class SpatialReference(Base):
    __tablename__ = 'SpatialReferences'
    __table_args__ = {u'schema': 'ODM2'}

    id = Column('SpatialReferenceID', Integer, primary_key=True)
    srs_id = Column('SRSID', String)
    srs_name = Column('SRSName', String)
    is_geographic = None
    #is_geographic = Column('IsGeographic', Boolean)
    notes = Column('Description', String)

    def __repr__(self):
        return "<SpatialReference('%s', '%s')>" % (self.id, self.srs_name)

sf_table = Samplingfeature().__table__
site_table = Site().__table__
site_join = site_table.join(sf_table, site_table.c.SamplingFeatureID == sf_table.c.SamplingFeatureID)
class Site2(Base):
    __tablename__ = u'Sites'
    __table__ = site_join


    id = site_join.c.ODM2_Sites_SamplingFeatureID
    code = site_join.c.ODM2_SamplingFeatures_SamplingFeatureCode
    name = site_join.c.ODM2_SamplingFeatures_SamplingFeatureName
    latitude = site_join.c.ODM2_Sites_Latitude
    longitude = site_join.c.ODM2_Sites_Longitude
    lat_long_datum_id = site_join.c.ODM2_Sites_LatLonDatumID._clone().foreign_keys = ForeignKey("SpatialReference.id")#, Integer, ForeignKey("SpatialReference.id"))#column_property(site_table.c.LatLonDatumID, ForeignKey('SpatialReference.id'))
    elevation_m = site_join.c.ODM2_SamplingFeatures_Elevation_m
    vertical_datum_id = site_join.c.ODM2_SamplingFeatures_ElevationDatumCV

    local_x = None
    local_y = None
    local_projection_id = None#Column('LocalProjectionID', Integer, ForeignKey('SpatialReferences.SpatialReferenceID'))
    pos_accuracy_m = None
    state = None
    county = None
    comments = None



    # relationships
    # TODO @sreeder, Please take a look at this line as it throws: sqlalchemy.exc.InvalidRequestError: Class <class 'ODM2.LikeODM1.model.Site2'> does not have a mapped column named 'lat_long_datum_id'
    # :)
    #spatial_ref = relationship(SpatialReference, primaryjoin=("SpatialReference.id==Site2.lat_long_datum_id"))
    #spatial_ref = relationship(SpatialReference)
    #spatial_ref = relationship(SpatialReference, primaryjoin="Site.lat_long_datum_id == SpatialReference.id")


    def __repr__(self):
        return "<Site('%s', '%s')>" % (self.code, self.name)

# ###################################################################################
#                            Units
# ###################################################################################

class Unit(Base):
    __tablename__ = u'Units'
    __table_args__ = {u'schema': 'ODM2'}

    id = Column('UnitsID', Integer, primary_key=True)
    name = Column('UnitsName', String)
    type = Column('UnitsTypeCV', String)
    abbreviation = Column('UnitsAbbreviation', String)

    def __repr__(self):
        return "<Unit('%s', '%s', '%s', '%s')>" % (self.id, self.name, self.type, self.abbreviation)

# ###################################################################################
#                            Variables
# ###################################################################################

"""Requires joining with Variable, Result, and Timeseriesresult to build Variable for ODM1_1_1"""
variables_table = Variable().__table__
ts_table = Timeseriesresult().__table__

result_table = Result().__table__
aliased_table = select([
    result_table.c.ResultID.label("RID"),
    result_table.c.UnitsID,
    result_table.c.VariableID,
    result_table.c.SampledMediumCV,
]).alias("ODM2_Aliased")

ts_join = aliased_table.join(ts_table, aliased_table.c.RID == ts_table.c.ResultID)
results = ts_join.join(variables_table, variables_table.c.VariableID == ts_join.c.ODM2_Aliased_RID)

class Variable(Base):
    __table__ = results
    __tablename__ = u'Variables'

    id = results.c.ODM2_Variables_VariableID                                            # Column('VariableID', Integer, primary_key=True)
    code = results.c.ODM2_Variables_VariableCode                                        # Column('VariableCode', String, nullable=False)
    name = results.c.ODM2_Variables_VariableNameCV                                      # Column('VariableNameCV', String, nullable=False)
    speciation = results.c.ODM2_Variables_SpeciationCV                                  # Column('SpeciationCV', String, nullable=False)
    no_data_value = results.c.ODM2_Variables_NoDataValue                                # Column('NoDataValue', Float, nullable=False)

    variable_unit_id = results.c.ODM2_Aliased_UnitsID                                   # Column('VariableUnitsID', Integer, ForeignKey('Units.UnitsID'), nullable=False)
    sample_medium = results.c.ODM2_Aliased_SampledMediumCV                              # Column('ODM2_Results_UnitsID', String, nullable=False)
    value_type = results.c.ODM2_Variables_VariableTypeCV                                # Column('ValueType', String, nullable=False)
    is_regular = None                                                                   # Column('IsRegular', Boolean, nullable=False)
    time_support = results.c.ODM2_TimeSeriesResults_IntendedTimeSpacing                 # Column('TimeSupport', Float, nullable=False)
    time_unit_id = results.c.ODM2_TimeSeriesResults_IntendedTimeSpacingUnitsID          # Column('TimeUnitsID', Integer, ForeignKey('Units.UnitsID'), nullable=False)
    data_type = results.c.ODM2_TimeSeriesResults_AggregationStatisticCV                 # Column('DataType', String, nullable=False)
    general_category = None                                                             # Column('GeneralCategory', String, nullable=False)

    """
    # relationships
    variable_unit = relationship(Unit, primaryjoin=(
    "Unit.id==Variable.variable_unit_id"))  # <-- Uses class attribute names, not table column names
    time_unit = relationship(Unit, primaryjoin=("Unit.id==Variable.time_unit_id"))
    """
    def __repr__(self):
        return "<Variable('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % \
               (self.id, self.code, self.name, self.speciation, self.no_data_value, self.variable_unit_id,
               self.sample_medium, self.value_type, self.time_support, self.time_unit_id, self.data_type)


# ###################################################################################
#                            Data Sources
# ###################################################################################

people_table = Person().__table__
affiliation_table = Affiliation().__table__
organization_table = Organization().__table__

aliased_table = select([
    people_table.c.PersonID.label("PID"),
    people_table.c.PersonFirstName,
    people_table.c.PersonMiddleName,
    people_table.c.PersonLastName,
]).alias("ODM2_Aliased")

affiliation_join = aliased_table.join(affiliation_table, affiliation_table.c.AffiliationID == aliased_table.c.PID)
results = affiliation_join.join(organization_table, affiliation_join.c.ODM2_Affiliations_OrganizationID == organization_table.c.OrganizationID)

class Source(Base):
    __table__ = results
    __tablename__ = u'Data Sources'
    __table_args__ = {u'schema': u'ODM2'}

    id = results.c.ODM2_Affiliations_AffiliationID                      # Column('OrganizationID', Integer, primary_key=True)
    organization = results.c.ODM2_Affiliations_OrganizationID           # Column('OrganizationName', String, nullable=False)
    description = results.c.ODM2_Organizations_OrganizationDescription  # Column('OrganizationDescription', String, nullable=False)
    link = results.c.ODM2_Organizations_OrganizationLink                # Column('OrganizationLink', String)

    first_name = results.c.ODM2_Aliased_PersonFirstName
    middle_name = results.c.ODM2_Aliased_PersonMiddleName
    last_name = results.c.ODM2_Aliased_PersonLastName
    # this doesnt work...
    # contact_name = column_property(first_name + " " + middle_name + " " + last_name)
    contact_name = column_property(first_name + " " + last_name)

    phone = results.c.ODM2_Affiliations_PrimaryPhone                    # Column('Phone', String, nullable=False)
    email = results.c.ODM2_Affiliations_PrimaryEmail                    # Column('Email', String, nullable=False)
    address = results.c.ODM2_Affiliations_PrimaryAddress                # Column('Address', String, nullable=False)
    city = "Unknown"                                                   # Column('City', String, nullable=False)
    state = "Unknown"                                                  # Column('State', String, nullable=False)
    zip_code = "Unknown"                                               # Column('ZipCode', String, nullable=False)
    citation = "Not specified"
    #iso_metadata_id = Column('MetadataID', Integer, ForeignKey('ODM2.ISOMetadata.MetadataID'), nullable=False)

    # relationships
    #iso_metadata = relationship(ISOMetadata)

    def __repr__(self):
        return "<Source('%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % \
               (self.id, self.contact_name, self.first_name, self.last_name,
                self.phone, self.organization, self.description)

class ISOMetadata(Base):
    __tablename__ = 'ISOMetadata'

    id = Column('MetadataID', Integer, primary_key=True)
    topic_category = Column('TopicCategory', String, nullable=False)
    title = Column('Title', String, nullable=False)
    abstract = Column('Abstract', String, nullable=False)
    profile_version = Column('ProfileVersion', String, nullable=False)
    metadata_link = Column('MetadataLink', String)

    def __repr__(self):
        return "<ISOMetadata('%s', '%s', '%s')>" % (self.id, self.topic_category, self.title)

# ###################################################################################
#                            Data Collection Methods
# ###################################################################################

method_table = Method().__table__

class LabMethod(Base):
    __tablename__ = 'LabMethods'

    id = Column('LabMethodID', Integer, primary_key=True)
    name = Column('LabName', String, nullable=False)
    organization = Column('LabOrganization', String, nullable=False)
    method_name = Column('LabMethodName', String, nullable=False)
    method_description = Column('LabMethodDescription', String, nullable=False)
    method_link = Column('LabMethodLink', String)

    def __repr__(self):
        return "<LabMethod('%s', '%s', '%s', '%s')>" % (self.id, self.name, self.organization, self.method_name)

class Method(Base):
    __table__ = method_table
    __tablename__ = u'Methods'
    __table_args__ = {u'schema': u'ODM2'}

    id = method_table.c.MethodID                            # Column('MethodID', Integer, primary_key=True)
    description = method_table.c.MethodDescription          # Column('MethodDescription', String, nullable=False)
    link = method_table.c.MethodLink                        # Column('MethodLink', String)

    def __repr__(self):
        return "<Method('%s', '%s', '%s')>" % (self.id, self.description, self.link)

# ###################################################################################
#                            ODMVersion
# ###################################################################################
class ODMVersion:
    #__tablename__ = 'ODMVersion'

    #version_number = Column('VersionNumber', String, primary_key=True)
    version_number = 2

    def __repr__(self):
        return "<ODMVersion('%s')>" % (self.version_number)

'''
class CensorCodeCV(Base):
    __tablename__ = 'cvterms'

    term = Column('Term', String, primary_key=True)
    definition = Column('Definition', String)

    def __repr__(self):
        return "<CensorCodeCV('%s', '%s')>" % (self.term, self.definition)

class DataTypeCV(Base):
    __tablename__ = 'cvterms'

    term = Column('Term', String, primary_key=True)
    definition = Column('Definition', String)

    def __repr__(self):
        return "<DataTypeCV('%s', '%s')>" % (self.term, self.definition)  # Declare a mapped class

class GeneralCategoryCV(Base):
    __tablename__ = 'cvterms'

    term = Column('Term', String, primary_key=True)
    definition = Column('Definition', String)

    def __repr__(self):
        return "<GeneralCategoryCV('%s', '%s')>" % (self.term, self.definition)

class SampleMediumCV(Base):
    __tablename__ = 'cvterms'

    term = Column('Term', String, primary_key=True)
    definition = Column('Definition', String)

    def __repr__(self):
        return "<SampleMedium('%s', '%s')>" % (self.term, self.definition)

class SampleTypeCV(Base):
    __tablename__ = 'cvterms'

    term = Column('Term', String, primary_key=True)
    definition = Column('Definition', String)

    def __repr__(self):
        return "<SampleTypeCV('%s', '%s')>" % (self.term, self.definition)

class SiteTypeCV(Base):
    __tablename__ = 'cvterms'

    term = Column('Term', String, primary_key=True)
    definition = Column('Definition', String)

    def __repr__(self):
        return "<SiteTypeCV('%s', '%s')>" % (self.term, self.definition)

class SpeciationCV(Base):
    __tablename__ = 'cvterms'

    term = Column('Term', String, primary_key=True)
    definition = Column('Definition', String)

    def __repr__(self):
        return "<SpeciationCV('%s', '%s')>" % (self.term, self.definition)

class TopicCategoryCV(Base):
    __tablename__ = 'cvterms'

    term = Column('Term', String, primary_key=True)
    definition = Column('Definition', String)

    def __repr__(self):
        return "<TopicCategoryCV('%s', '%s')>" % (self.term, self.definition)

class ValueTypeCV(Base):
    __tablename__ = 'cvterms'

    term = Column('Term', String, primary_key=True)
    definition = Column('Definition', String)

    def __repr__(self):
        return "<ValueTypeCV('%s', '%s')>" % (self.term, self.definition)

class VariableNameCV(Base):
    __tablename__ = 'cvterms'

    term = Column('Term', String, primary_key=True)
    definition = Column('Definition', String)

    def __repr__(self):
        return "<VariableNameCV('%s', '%s')>" % (self.term, self.definition)

class VerticalDatumCV(Base):
    __tablename__ = 'cvterms'

    term = Column('Term', String, primary_key=True)
    definition = Column('Definition', String)

    def __repr__(self):
        return "<VerticalDatumCV('%s', '%s')>" % (self.term, self.definition)
'''
class Sample(Base):
    __tablename__ = 'Samples'

    id = Column('SampleID', Integer, primary_key=True)
    type = Column('SampleType', String, nullable=False)
    lab_sample_code = Column('LabSampleCode', String, nullable=False)
    lab_method_id = Column('LabMethodID', Integer, ForeignKey('ODM2.LabMethods.LabMethodID'), nullable=False)

    # relationships
    #lab_method = relationship(LabMethod)

    def __repr__(self):
        return "<Sample('%s', '%s', '%s', '%s')>" % (self.id, self.type, self.lab_sample_code, self.lab_method_id)

class Qualifier(Base):
    __tablename__ = u'Annotations'
    __table_args__ = {u'schema': u'ODM2'}

    id = Column('AnnotationID', Integer, primary_key=True)
    code = Column('AnnotationCode', String, nullable=False)
    description = Column('AnnotationText', String, nullable=False)

    def __repr__(self):
        return "<Qualifier('%s', '%s', '%s')>" % (self.id, self.code, self.description)

#TODO Table no longer exists
class OffsetType(Base):
    
    __tablename__ = u'TimeSeriesResults'
    __table_args__ = {u'schema': 'ODM2'}

    id = Column('OffsetTypeID', Integer, primary_key=True)
    unit_id = Column('ZLocationUnitsID', Integer, ForeignKey('ODM2.Units.UnitsID'), nullable=False)
    description = Column('OffsetDescription', String)

    # relationships
    unit = relationship(Unit)

    def __repr__(self):
        return "<Unit('%s', '%s', '%s')>" % (self.id, self.unit_id, self.description)


class QualityControlLevel(Base):
    __tablename__ = u'ProcessingLevels'
    __table_args__ = {u'schema': u'ODM2'}

    id = Column('ProcessingLevelID', Integer, primary_key=True)
    code = Column('ProcessingLevelCode', String, nullable=False)
    definition = Column('Definition', String, nullable=False)
    explanation = Column('Explanation', String, nullable=False)

    def __repr__(self):
        return "<QualityControlLevel('%s', '%s', '%s', '%s')>" % (self.id, self.code, self.definition, self.explanation)


'''
def copy_data_value(from_dv):
    new = DataValue()
    new.data_value = from_dv.data_value
    new.value_accuracy = from_dv.value_accuracy
    new.local_date_time = from_dv.local_date_time
    new.utc_offset = from_dv.utc_offset
    new.date_time_utc = from_dv.date_time_utc
    new.site_id = from_dv.site_id
    new.variable_id = from_dv.variable_id
    new.offset_value = from_dv.offset_value
    new.offset_type_id = from_dv.offset_type_id
    new.censor_code = from_dv.censor_code
    new.qualifier_id = from_dv.qualifier_id
    new.method_id = from_dv.method_id
    new.source_id = from_dv.source_id
    new.sample_id = from_dv.sample_id
    new.derived_from_id = from_dv.derived_from_id
    new.quality_control_level_id = from_dv.quality_control_level_id
    return new
'''
'''
class DataValue(Base):
    __tablename__ = 'DataValues'

    id = Column('ValueID', Integer, primary_key=True)
    data_value = Column('DataValue', Float)
    value_accuracy = Column('ValueAccuracy', Float)
    local_date_time = Column('LocalDateTime', DateTime)
    utc_offset = Column('UTCOffset', Float)
    date_time_utc = Column('DateTimeUTC', DateTime)
    site_id = Column('SiteID', Integer, ForeignKey('Sites.SiteID'), nullable=False)
    variable_id = Column('VariableID', Integer, ForeignKey('Variables.VariableID'), nullable=False)
    offset_value = Column('OffsetValue', Float)
    offset_type_id = Column('OffsetTypeID', Integer, ForeignKey('OffsetTypes.OffsetTypeID'))
    censor_code = Column('CensorCode', String)
    qualifier_id = Column('QualifierID', Integer, ForeignKey('Qualifiers.QualifierID'))
    method_id = Column('MethodID', Integer, ForeignKey('Methods.MethodID'), nullable=False)
    source_id = Column('SourceID', Integer, ForeignKey('Sources.SourceID'), nullable=False)
    sample_id = Column('SampleID', Integer, ForeignKey('Samples.SampleID'))
    derived_from_id = Column('DerivedFromID', Integer)
    quality_control_level_id = Column('QualityControlLevelID', Integer,
                                      ForeignKey('QualityControlLevels.QualityControlLevelID'), nullable=False)

    # relationships
    site = relationship(Site)
    variable = relationship(Variable)
    method = relationship(Method)
    source = relationship(Source)
    quality_control_level = relationship(QualityControlLevel)

    qualifier = relationship(Qualifier)
    offset_type = relationship(OffsetType)
    sample = relationship(Sample)

    def list_repr(self):
        return [self.id, self.data_value, self.value_accuracy, self.local_date_time,
                self.utc_offset, self.date_time_utc, self.site_id, self.variable_id,
                self.offset_value, self.offset_type_id, self.censor_code, self.qualifier_id,
                self.method_id, self.source_id, self.sample_id, self.derived_from_id,
                self.quality_control_level_id]

    def __repr__(self):
        return "<DataValue('%s', '%s', '%s')>" % (self.data_value, self.local_date_time, self.value_accuracy)

def copy_series(from_series):
    new = Series()
    new.site_id = from_series.site_id
    new.site_code = from_series.site_code
    new.site_name = from_series.site_name
    new.variable_id = from_series.variable_id
    new.variable_code = from_series.variable_code
    new.variable_name = from_series.variable_name
    new.speciation = from_series.speciation
    new.variable_units_id = from_series.variable_units_id
    new.variable_units_name = from_series.variable_units_name
    new.sample_medium = from_series.sample_medium
    new.value_type = from_series.value_type
    new.time_support = from_series.time_support
    new.time_units_id = from_series.time_units_id
    new.time_units_name = from_series.time_units_name
    new.data_type = from_series.data_type
    new.general_category = from_series.general_category
    new.method_id = from_series.method_id
    new.method_description = from_series.method_description
    new.source_id = from_series.source_id
    new.organization = from_series.organization
    new.citation = from_series.citation
    new.quality_control_level_id = from_series.quality_control_level_id
    new.quality_control_level_code = from_series.quality_control_level_code
    new.begin_date_time = from_series.begin_date_time
    new.begin_date_time_utc = from_series.begin_date_time_utc
    new.end_date_time_utc = from_series.end_date_time_utc
    new.value_count = from_series.value_count
    return new
'''
'''
class SeriesCatalog(Base):
    __tablename__ = 'SeriesCatalog'

    id = Column('SeriesID', Integer, primary_key=True)
    site_id = Column('SiteID', Integer, ForeignKey('Sites.SiteID'), nullable=False)
    site_code = Column('SiteCode', String)
    site_name = Column('SiteName', String)
    variable_id = Column('VariableID', Integer, ForeignKey('Variables.VariableID'), nullable=False)
    variable_code = Column('VariableCode', String)
    variable_name = Column('VariableName', String)
    speciation = Column('Speciation', String)
    variable_units_id = Column('VariableUnitsID', Integer)
    variable_units_name = Column('VariableUnitsName', String)
    sample_medium = Column('SampleMedium', String)
    value_type = Column('ValueType', String)
    time_support = Column('TimeSupport', Float)
    time_units_id = Column('TimeUnitsID', Integer)
    time_units_name = Column('TimeUnitsName', String)
    data_type = Column('DataType', String)
    general_category = Column('GeneralCategory', String)
    method_id = Column('MethodID', Integer, ForeignKey('Methods.MethodID'), nullable=False)
    method_description = Column('MethodDescription', String)
    source_id = Column('SourceID', Integer, ForeignKey('Sources.SourceID'), nullable=False)
    source_description = Column('SourceDescription', String)
    organization = Column('Organization', String)
    citation = Column('Citation', String)
    quality_control_level_id = Column('QualityControlLevelID', Integer,
                                      ForeignKey('QualityControlLevels.QualityControlLevelID'), nullable=False)
    quality_control_level_code = Column('QualityControlLevelCode', String)
    begin_date_time = Column('BeginDateTime', DateTime)
    end_date_time = Column('EndDateTime', DateTime)
    begin_date_time_utc = Column('BeginDateTimeUTC', DateTime)
    end_date_time_utc = Column('EndDateTimeUTC', DateTime)
    value_count = Column('ValueCount', Integer)

    data_values = relationship("DataValue",
                               primaryjoin="and_(DataValue.site_id == Series.site_id, "
                                           "DataValue.variable_id == Series.variable_id, "
                                           "DataValue.method_id == Series.method_id, "
                                           "DataValue.source_id == Series.source_id, "
                                           "DataValue.quality_control_level_id == Series.quality_control_level_id)",
                               foreign_keys="[DataValue.site_id, DataValue.variable_id, DataValue.method_id, DataValue.source_id, DataValue.quality_control_level_id]",
                               order_by="DataValue.local_date_time",
                               backref="series")

    site = relationship(Site)
    variable = relationship(Variable)
    method = relationship(Method)
    source = relationship(Source)
    quality_control_level = relationship(QualityControlLevel)

    # TODO add all to repr
    def __repr__(self):
        return "<Series('%s')>" % (self.id)

    def get_table_columns(self):
        return self.__table__.columns.keys()

'''