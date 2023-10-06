def _mapQuestions(args):
    """
    This function initializes the mapping.

    Args:
        userID (str): User ID.
        mapUUID (str): Map UUID.
        inputFilename (str): Input Filename.
        configuration (dict): Mapping configuration.
        order (int): Order of the mapping.

    Raises:
        ErrorHandler: A user defined exception which throws FILE_NOT_FOUND_SERVER error if output file not found on the server.
    """
    try:

        userID = args.get("userID")
        mapUUID = args.get("mapUUID")
        inputFilename = args.get("inputFilename")
        configuration = args.get("configuration")
        order = args.get("order")

        print(f"{str(order).zfill(3)} | {userID} | {mapUUID} | Mapping started")

        # mappingInProgress.acquire()

        mappingManager = MappingManager()
        dbHelper = DBHelper()
        fileHelper = FileHelper()

        # Downloading input file from S3
        inputFile = fileHelper.downloadInputfile(
            userID, mapUUID, inputFilename)

        mappingManager.mapQuestions(mapUUID, inputFile, configuration)

        # Writing to question the file and uploading output file to S3
        outputFilename = mappingManager.writeQuestionnaire(userID, mapUUID, inputFile,
                                                           configuration.get("excel_sheet"))

        if not outputFilename:
            raise ErrorHandler("App", "mapQuestions",
                               AMPErrors.FILE_NOT_FOUND_SERVER)

        # Creating map record in the database
        dbHelper.createMapRecord(userID, mapUUID, outputFilename, configuration,
                                 mappingManager.questionnaire.questions)

        # Deleting local file after use
        shutil.rmtree(os.path.join(Constants.DOWNLOAD_FOLDER,
                      mapUUID), onerror=_removeDirectoryError)

        # mappingInProgress.release()
        print(f"{str(order).zfill(3)} | {userID} | {mapUUID} | Mapping completed")

    except Exception as error:
        # mappingInProgress.release()
        logging.error(error)


@app.route("/", methods=["GET", "POST"])
@cross_origin()
def home():
    if not is_authorized(request):
        return "Unauthorized Request", 401
    return render_template("./index.html")
