import birdnet


def predict(species_list, path):
	model = birdnet.load("acoustic", "2.4", "tf")
	predictions = model.predict(
		path,
		# predict only the species from the file
		custom_species_list=species_list,
	)
	return predictions.to_csv()