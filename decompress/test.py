def reconstructDataMulti_with_correlation(atoms_coded_tricklets, corr_coded_tricklets, Dictionary, ts):
    # result = [[] for i in range(len(sparseData))]
    # print(sparseData)

    result = {}

    # print(atoms_coded_tricklets)
    # input('')
    # start with reconstructing the atoms stored tricklets
    # for each time series
    for k, v in atoms_coded_tricklets.items():
        out = {}
        # print(sparseData[index])
        # print()
        for w in sorted(v.keys()):
            # print(t)
            sum = np.zeros(Dictionary.T.shape[0])

            for i, e in v[w]:
                # print(Dictionary.T[:,int(i)])
                # print(e)
                # print('\n')
                sum += Dictionary.T[:, int(i)] * e

            out[w] = sum.tolist()

            # print(out)
        # print(out)
        result[k] = out
        # print(result)

    # out.append(np.sum(Dictionary.T * sparseData[n], axis=1))
    # for k, v in result.items():
    #     # print(k, v.keys())
    #     for j in v.keys():
    #         try:
    #             print(ts[k][j])
    #             print(result[k][j])
    #
    #             plt.plot(ts[k][j])
    #             plt.plot(result[k][j])
    #             plt.title(str(i) + '_' + str(j))
    #             plt.show()
    #             print()
    #         except:
    #             print()
    #     print()

    # for each TS stored using correlation
    for k in corr_coded_tricklets.keys():
        # for each window and shift value
        for w in corr_coded_tricklets[k].keys():
            i_m = corr_coded_tricklets[k][w]
            # i_m, shift = corr_coded_tricklets[k][w]
            # print(shift)
            if k not in result.keys():
                result[k] = {}
            result[k][w] = [x  for x in result[i_m][w]]
            # result[k][w] = [x + shift for x in result[i_m][w]]

            # print(ts[k][w])
            # print(result[k][w])

            # plt.plot(ts[k][w])
            # plt.plot(result[k][w])
            # plt.plot(result[i_m][w])
            # plt.title(str(i) + '_' + str(w))
            # plt.show()
            # print('yep')

            # print()
            # try:
            #     # print(atoms_coded_tricklets[value][key])
            # print('a is ', a)
            # print(atoms_coded_tricklets[i_m][w] * a )
            # print(atoms_coded_tricklets[i_m][w] )

            # found_list, shift = find_corr_list(result, corr_coded_tricklets, i_m, w, shift)

            # corr_i = result[corr_coded_tricklets[value][w]][w]

            # print("XXXXXXX", index)
            # result[k][w] = [x + shift for x in result[i_m][w]]

            # try:
            #     result[index][w] = [x + shift for x in result[i_m][w]]
            # except:
            #     result[index][w] = [x + shift for x in result[corr_coded_tricklets[index][w]][w]]

            # except:
            #     result[index][w] = result[corr_coded_tricklets[value][w]][w]
            # not complete, it fixes a one way run, but not all cases
            # print(key)

    # print(len(out))
    # print(len(result[0]))

    resultList = []
    for i in range(len(result.values())):
        # li =
        # v = result[i]
        resultList.append([result[i][j] for j in sorted(result[i].keys())])

        # for j in range(len(result[i])):
        #     plt.plot(ts[i][j])
        #     plt.plot(resultList[i][j])
        #     plt.title(str(i) + '_' + str(j))
        #     plt.show()

        # resultList.append(li)

    # print(len(result))
    # for k in range(len(result.items())):
    #     w_list = [[] in range(len(result[k]))]
    #     print(w_list)
    #
    #     resultList[k] = [x for x in v.values()]
    #
    # for j in range(len(ts[k])):
    #     plt.plot(ts[k][j])
    #     plt.plot(resultList[k][j])
    #     plt.title(str(k) + '_'+str(j))
    #     plt.show()
    #
    #     print()

    return resultList

def sparse_code_with_correlation(ts, correlation_matrix, Dictionary, nonzero_coefs, transform_algorithm, threshold):
    """

    :type correlation_matrix: object
    """

    from sklearn.decomposition import SparseCoder

    coder = SparseCoder(dictionary=Dictionary, transform_n_nonzero_coefs=nonzero_coefs,
                        transform_alpha=None, transform_algorithm=transform_algorithm)

    # For each time series, for each tricklet, transform the tricklet and store it
    result = []
    for t in ts:
        result.append(coder.transform(t))

    # tricklets sparsely coded
    tricklets = []

    # transform sparse matrix into sparse arrays
    for index in range(len(result)):
        temp = []
        for t in range(result[index].shape[0]):
            x = []
            for i, e in enumerate(result[index][t]):
                if e != 0:
                    x.append([i, e])
            temp.append(x)
        tricklets.append(temp)
    for index in range(len(result)):
        tricklets[index] = np.array([np.array(xi) for xi in tricklets[index]])

    atoms_coded_tricklets = {}
    # atoms_coded_tricklets = [{} for i in range(len(ts))
    corr_coded_tricklets = {}

    # print('corr size:', get_size(corr_coded_tricklets))

    # for each time window
    for w in range(result[0].shape[0]):
        # create dictionary to keep indices
        A = correlation_matrix[w].values.tolist()
        B = {i: A[i] for i in range(len(A))}
        # sort lines in a decent order by the sum of their elements
        C = dict(sorted(B.items(), key=lambda i: sum(i[1]), reverse=True))

        i_stored = []

        x_plotting = np.array([])
        y_plotting = np.array([])
        # for each line (TS)
        # print('shift reduced error?')

        # shift_works = []

        # for each time series
        for k, X in C.items():

            # Find the index maximizing the correlation
            # m =   list of indices of corr TS candidates AND
            #       already stored normally and different than itself
            m = {i: v for i, v in enumerate(X) if (
                    i in i_stored and v >= threshold and k != i)}
            m = dict(sorted(m.items(), key=lambda i: i[1], reverse=True))

            try:
                i_m = list(m.keys())[0]
            except:
                i_m = None

            # i_m = [i for i, v in enumerate(X) if m and v == max(m)]  # indice of the max
            # if k == 2 and w == 53:

            # print('m =', m, ', i_m=', i_m, ', i_stored=', i_stored)
            if i_m is not None:  # store corr
                # print('first in ')
                # i_m = i_m[0]
                x = ts[i_m][w]
                y = ts[k][w]
                if k not in corr_coded_tricklets.keys():
                    corr_coded_tricklets[k] = {}
                # corr_coded_tricklets[k][w] = i_m, shift_mean(x, y)
                corr_coded_tricklets[k][w] = i_m
                # print(shift_mean(x, y))

                # z = [v + shift_mean(x, y) for v in x]
                z = [v for v in x]
                # shift_works.append(mse(x, y) > mse(x, z))
                # plt.plot(x)
                # plt.plot(y)

                # plt.plot(z)
                # plt.savefig('outputs/shift_plots/shift_plots%d_%d.png' % (k, w))
                # plt.show()
                # plt.cla()
                # print(((np.array(x) - np.array(y)) ** 2).mean(axis=None))
                # np.append(x_plotting, shift_mean(x, y))
                # np.append(y_plotting, mse(x,y))
                # input('')
                # a, b = alpha_beta(x, y)
                # if a != 0 :
                #     corr_coded_tricklets[k][w] = i_m, a, b  # pick the first candidate maximizing the correlation
                # else:
                #     if k in atoms_coded_tricklets:
                #         atoms_coded_tricklets[k][w] = tricklets[k][w]
                #     else:
                #         atoms_coded_tricklets[k] = {}
                #         atoms_coded_tricklets[k][w] = tricklets[k][w]
                #     i_stored.append(k)
            else:  # store sparse
                # print('2nd in ')
                if k not in atoms_coded_tricklets:
                    atoms_coded_tricklets[k] = {}
                atoms_coded_tricklets[k][w] = tricklets[k][w]
                # add k to the list of elements stored in sparse way
                i_stored.append(k)

        #  plt.cla()
        #  plt.xlabel('shift mean')
        #  plt.ylabel('error')
        #  plt.title('shift mean vs mserror')
        #  plt.scatter(x, y)
        # # plt.show()
        #  plt.savefig('outputs/shift_error/shift_vs_error%d.png'%w)
        # print('yeah', any(item == True for item in shift_works))

    # print(atoms_coded_tricklets)
    # print(corr_coded_tricklets)
    return atoms_coded_tricklets, corr_coded_tricklets

def compress_with_correlation(ts, correlation_matrix, Dictionary, corr_threshold, nbAtoms, transform_algorithm):
    # Transforming test data into sparse respresentation using the omp algorithm

    print("Transforming test data into correlation-aware sparse respresentation ... ", end='')
    atoms_coded_tricklets, corr_coded_tricklets = sparse_code_with_correlation(ts, correlation_matrix, Dictionary,
                                                                               nbAtoms, transform_algorithm,
                                                                               corr_threshold)

    # sparseData = sparse_code_without_correlation(ts, Dictionary, nbAtoms, "omp")
    # print(atoms_coded_tricklets)

    print("done!")

    print("Reconstructing data with correlation...", end="")

    # print(corr_coded_tricklets)

    # for k,v in corr_coded_tricklets.items():
    #     print(k, v)

    recons = reconstructDataMulti_with_correlation(atoms_coded_tricklets, corr_coded_tricklets, Dictionary, ts)
    print("done!")
    # # print(recons)

    # print(corr_coded_tricklets)

    import itertools

    errors = []
    result_before = []
    result_after = []
    # print("Error's norm of the correlation-aware method: ", end="")
    for i in range(len(ts)):
        errors.append(calculate_RMSE(ts[i], recons[i]))
        # print(i)
        result_before.append(list(itertools.chain.from_iterable(ts[i])))
        result_after.append(list(itertools.chain.from_iterable(recons[i])))
        #
        # print(len(result))
        # print(len(result[0]))

    result_after = pd.DataFrame(result_after)
    result_before = pd.DataFrame(result_before)
    result_before = result_before.T
    result_after = result_after.T
    print(result_before.shape)
    print(result_after.shape)
    print(result_before.head())
    print(result_after.head())


    result_after.to_csv('yoga_after.txt', float_format='%.6f', header=False, sep=' ', index=False)
    result_before.to_csv('yoga_before.txt', float_format='%.6f', header=False, sep=' ', index=False)

        # errors.append(np.square(np.array(normalized(ts[i]) - np.array(normalized(recons[i]))) ** 2).mean(axis=None))
        # for j in range(len(ts[i])):
        # try:
        # plt.plot(ts[i][j])
        # plt.plot(recons[i][j])
        # plt.title(str(i) + '_'+str(j))
        # plt.show()

        # except:
        #     print()
        #
        #     try:
        #         print(corr_coded_tricklets[i][j])
        #     except:
        #         print('in atoms')
        #     plt.show()

        # errors.append(calculate_RMSE(ts[i], np.array(recons[i])))
    # print(errors)

    return atoms_coded_tricklets, corr_coded_tricklets, errors

    # plt.plot(errors)
    # plt.ylabel('errors')
    # plt.show()