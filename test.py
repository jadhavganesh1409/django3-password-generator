def getMapData():
    """
    _summary_

    Raises:
        ErrorHandler: _description_
        ErrorHandler: _description_
        ErrorHandler: _description_
        ErrorHandler: _description_
        ErrorHandler: _description_

    Returns:
        _type_: _description_
    """
    try:
        if not is_authorized(request):
            return "Unauthorized Request", 401

        body = request.args
        userID = body.get("user_id")
        mapUUID = body.get("map_uuid")
        outputFilename = body.get("output_filename")
        config = unquote(body.get("configuration")) if body.get(
            "configuration") else {}

        if not userID:
            raise ErrorHandler("App", "getMapData",
                               AMPErrors.USER_ID_NOT_FOUND)
        if not mapUUID:
            raise ErrorHandler("App", "getMapData",
                               AMPErrors.MAP_UUID_NOT_FOUND)
        if not outputFilename:
            raise ErrorHandler("App", "getMapData",
                               AMPErrors.FILE_NOT_FOUND)
        if not config:
            raise ErrorHandler("App", "getMapData",
                               AMPErrors.CONFIG_NOT_FOUND)
        try:
            config = json.loads(config)
        except ValueError as error:
            raise ErrorHandler("App", "getMapData",
                               AMPErrors.INVALID_CONFIG)

        configuration = {}
        configuration["excel_sheet"] = config.get("excel_sheet") \
            if config.get("excel_sheet") else None
        configuration["question_column"] = ord(str(config.get("question_column")).lower()) - 96 \
            if config.get("question_column") and not config.get("question_column").isnumeric() else config.get("question_column")
        configuration["risk_vector_column"] = ord(str(config.get("risk_vector_column")).lower()) - 96 \
            if config.get("risk_vector_column") and not config.get("risk_vector_column").isnumeric() else config.get("risk_vector_column")
        configuration["context_column"] = ord(str(config.get("risk_vector_column")).lower()) - 96 \
            if config.get("context_column") and not config.get("context_column").isnumeric() else config.get("context_column")
        configuration["add_to_db"] = True \
            if config.get("add_to_db") and isinstance(config.get("add_to_db"), bool) else False
        configuration["map_risk_vectors"] = True \
            if config.get("map_risk_vectors") and isinstance(config.get("map_risk_vectors"), bool) else False
        configuration["map_contexts"] = True \
            if config.get("map_contexts") and isinstance(config.get("map_contexts"), bool) else False

        fileHelper = FileHelper()

        outputFile = fileHelper.downloadOutputfile(
            userID,
            mapUUID,
            outputFilename,
        )

        workbook = load_workbook(outputFile)
        sheet = workbook[configuration.get("excel_sheet")]
        questions = []

        for row in sheet.iter_rows(values_only=True):
            questions.append({
                "question_id": row[0],
                "question": row[3],
                "risk_vectors": row[4],
                "context": row[5],
                "status": row[6],
                "accuracy": row[9]
            })

        workbook.close()
      
        print('mapUUID getMapData'+mapUUID)
        shutil.rmtree(os.path.join(Constants.DOWNLOAD_FOLDER,
                      mapUUID), onerror=_removeDirectoryError)

        return _getSuccessResponse({
            "user_id": userID,
            "map_uuid": mapUUID,
            "output_filename": outputFilename,
            "configuration": configuration,
            "map_data": questions[1:],
        })
    except Exception as error:
        logging.error(error)
        return _getErrorResponse(error)
