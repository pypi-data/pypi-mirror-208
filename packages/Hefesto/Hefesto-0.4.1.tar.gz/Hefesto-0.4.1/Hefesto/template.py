
class Template:

  template_model = dict(

    Age = dict(
      process_type = "http://purl.obolibrary.org/obo/NCIT_C142470",
      output_type = "http://purl.obolibrary.org/obo/NCIT_C70856",
      attribute_type = "http://purl.obolibrary.org/obo/NCIT_C25150",
      value_datatype = "xsd:date",
      startdate = None,
      enddate = None,
      pid = None,
      context_id = None
    ),

    Birthdate = dict(
      process_type = "http://purl.obolibrary.org/obo/NCIT_C142470",
      output_type = "http://purl.obolibrary.org/obo/NCIT_C70856",
      attribute_type = "http://purl.obolibrary.org/obo/NCIT_C68615",
      value_datatype = "xsd:date",
      startdate = None,
      enddate = None,
      pid = None,
      context_id = None
    ),

    Deathdate = dict( 
      process_type= "http://purl.obolibrary.org/obo/NCIT_C142470",
      output_type= "http://purl.obolibrary.org/obo/NCIT_C70856",
      attribute_type = "http://purl.obolibrary.org/obo/NCIT_C70810",
      value_datatype = "xsd:date",
      startdate = None,
      enddate = None,
      pid = None,
      context_id = None
    ),

    First_visit = dict(
      process_type = "http://purl.obolibrary.org/obo/NCIT_C142470",
      output_type = "http://purl.obolibrary.org/obo/NCIT_C70856",
      attribute_type = "http://purl.obolibrary.org/obo/NCIT_C164021",
      value_datatype = "xsd:date",
      startdate = None,
      enddate = None,
      pid = None,
      context_id = None
    ),

    Sex = dict( 
      process_type = "http://purl.obolibrary.org/obo/NCIT_C142470",
      output_type = "http://purl.obolibrary.org/obo/NCIT_C70856",
      attribute_type = "http://purl.obolibrary.org/obo/NCIT_C28421",
      value_datatype = "xsd:string",
      startdate = None,
      enddate = None,
      pid = None,
      context_id = None
    ),


    Status = dict(
      process_type = "http://purl.obolibrary.org/obo/NCIT_C142470",
      output_type = "http://purl.obolibrary.org/obo/NCIT_C70856",
      attribute_type = "http://purl.obolibrary.org/obo/NCIT_C166244",
      value_datatype = "xsd:string",
      startdate = None,
      enddate = None,
      pid = None,
      context_id = None
    ),

    Diagnosis = dict(
      process_type= "http://purl.obolibrary.org/obo/NCIT_C15220",
      output_type= "http://purl.obolibrary.org/obo/NCIT_C70856",
      attribute_type= "http://purl.obolibrary.org/obo/NCIT_C2991",
      value_datatype = "xsd:string",
      startdate = None,
      enddate = None,
      pid = None,
      context_id = None
    ),

    # Onset_diagnosis = dict(
    #   process_type= "http://purl.obolibrary.org/obo/NCIT_C142470",
    #   output_type = "http://purl.obolibrary.org/obo/NCIT_C70856",
    #   attribute_type= "http://purl.obolibrary.org/obo/NCIT_C164339",
    #   value_datatype = "xsd:date",
    #   startdate = None,
    #   enddate = None,
    #   pid = None,
    #   context_id = None
    # ),

    Onset_symptoms = dict(
      process_type= "http://purl.obolibrary.org/obo/NCIT_C142470",
      output_type = "http://purl.obolibrary.org/obo/NCIT_C70856",
      attribute_type= "http://purl.obolibrary.org/obo/NCIT_C124353",
      value_datatype = "xsd:date",
      startdate = None,
      enddate = None,
      pid = None,
      context_id = None
    ),

    # Phenotype = dict(
    #   process_type= "http://purl.obolibrary.org/obo/NCIT_C25305",
    #   output_type= "http://purl.obolibrary.org/obo/NCIT_C125204",
    #   attribute_type= "http://semanticscience.org/resource/SIO_010056",
    #   attribute_id = None,
    #   value_string= None,
    #   value_datatype = None,
    #   startdate = None,
    #   enddate = None,
    #   pid = None,
    #   context_id = None
    # ),

    Genetic = dict(
      process_type= "http://purl.obolibrary.org/obo/NCIT_C15709",
      output_type= "http://purl.obolibrary.org/obo/NCIT_C70856",
      attribute_type= "http://purl.obolibrary.org/obo/NCIT_C103223",
      value_datatype = "xsd:string",
      startdate = None,
      enddate = None,
      pid = None,
      context_id = None
    ),

    # Genotype_OMIM = dict(
    #   process_type= "http://purl.obolibrary.org/obo/NCIT_C15709",
    #   output_type= "http://purl.obolibrary.org/obo/NCIT_C16612",
    #   attribute_type= "http://edamontology.org/data_1153",
    #   attribute_id = None,
    #   value_string= None,
    #   value_datatype = None,
    #   startdate = None,
    #   enddate = None,
    #   pid = None,
    #   context_id = None
    # ),

    # Genotype_HGNC = dict(
    #   process_type= "http://purl.obolibrary.org/obo/NCIT_C15709",
    #   output_type= "http://purl.obolibrary.org/obo/NCIT_C16612",
    #   attribute_type= "http://edamontology.org/data_2298",
    #   attribute_id = None,
    #   value_string= None,
    #   value_datatype = None,
    #   startdate = None,
    #   enddate = None,
    #   pid = None,
    #   context_id = None
    # ),

    # Consent = dict(
    #   process_type= "http://purl.obolibrary.org/obo/OBI_0000810",
    #   output_type = None,
    #   attribute_type= "http://purl.obolibrary.org/obo/NCIT_C25460",
    #   attribute_id = None,
    #   value_string= None,
    #   value_datatype = None,
    #   startdate = None,
    #   enddate = None,
    #   pid = None,
    #   context_id = None
    # ),

    Consent_contacted = dict(
      process_type= "http://purl.obolibrary.org/obo/OBI_0000810",
      output_type = "http://purl.obolibrary.org/obo/OBIB_0000488",
      attribute_type= "http://purl.obolibrary.org/obo/NCIT_C25460",
      value_datatype = "xsd:string",
      startdate = None,
      enddate = None,
      pid = None,
      context_id = None
    ),

    Consent_used = dict(
      process_type= "http://purl.obolibrary.org/obo/OBI_0000810",
      output_type = "http://purl.obolibrary.org/obo/DUO_0000001",
      attribute_type= "http://purl.obolibrary.org/obo/NCIT_C25460",
      value_datatype = "xsd:string",
      startdate = None,
      enddate = None,
      pid = None,
      context_id = None
    ),

    Biobank = dict(
      process_type= "http://purl.obolibrary.org/obo/OMIABIS_0000061",
      output_type= "http://purl.obolibrary.org/obo/NCIT_C115570",
      attribute_type= "http://purl.obolibrary.org/obo/NCIT_C25429",
      value_datatype = "xsd:string",
      startdate = None,
      enddate = None,
      pid = None,
      context_id = None
    ),

    Disability = dict(
      process_type = None,
      output_type = "http://purl.obolibrary.org/obo/NCIT_C70856",
      attribute_type = "http://purl.obolibrary.org/obo/NCIT_C21007",
      value_datatype = "xsd:float",
      startdate = None,
      enddate = None,
      pid = None,
      context_id = None
    ),

    Body_measurement = dict(
      process_type = "http://purl.obolibrary.org/obo/NCIT_C142470" ,
      output_type=  "http://purl.obolibrary.org/obo/NCIT_C70856" ,
      value_datatype= "xsd:float" ,
      startdate= None ,
      enddate= None ,
      comments= None ,
      pid= None ,
      context_id= None 
    ),


    Lab_measurement = dict(
      process_type = "http://purl.obolibrary.org/obo/NCIT_C25294" ,
      output_type = "http://purl.obolibrary.org/obo/NCIT_C70856" ,
      value_datatype= "xsd:float" ,
      startdate= None ,
      enddate= None ,
      comments= None ,
      pid= None ,
      context_id= None 
    ),


    Imaging = dict(
      process_type = None ,
      output_type =  "http://purl.obolibrary.org/obo/NCIT_C70856" ,
      value_datatype = "xsd:string" ,
      startdate= None ,
      enddate= None ,
      comments= None ,
      pid = None ,
      context_id= None 
    ),


    Surgery = dict(
      value_datatype = "xsd:string" ,
      startdate= None ,
      enddate= None ,
      comments= None ,
      pid= None ,
      context_id= None 
    ),


    Clinical_trial = dict(
      process_type = "http://purl.obolibrary.org/obo/NCIT_C71104" ,
      output_type=  "http://purl.obolibrary.org/obo/NCIT_C115575" ,
      attribute_type= "http://purl.obolibrary.org/obo/NCIT_C2991" ,
      agent_type = "http://purl.obolibrary.org/obo/NCIT_C16696" ,
      value_datatype= "xsd:string",
      startdate= None ,
      enddate= None ,
      comments= None ,
      pid= None ,
      context_id= None
    ),


    Medications = dict(
      process_type = "http://purl.obolibrary.org/obo/NCIT_C25409",
      output_type =  "http://purl.obolibrary.org/obo/NCIT_C459" ,
      agent_type = "http://purl.obolibrary.org/obo/NCIT_C177929",
      value_datatype= "xsd:float",
      startdate= None ,
      enddate = None ,
      comments = None ,
      pid = None ,
      context_id = None 
    )


  )

