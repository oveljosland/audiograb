import birdnet

model = birdnet.load("acoustic", "2.4", "tf")

predictions = model.predict(
  "../../testmedia/test.wav",
  # predict only the species from the file
  custom_species_list="../config/species.txt",
)

predictions.to_csv("example/predictions.csv")